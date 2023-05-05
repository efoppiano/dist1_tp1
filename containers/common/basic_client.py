import json
import logging
import signal
import threading
from abc import ABC, abstractmethod
from typing import List, Iterator

import zmq
from zmq.sugar.context import ST

from common.packet_factory import PacketFactory, DIST_MEAN_REQUEST, DUR_AVG_REQUEST, TRIP_COUNT_REQUEST
from common.packets.dur_avg_out import DurAvgOut
from common.packets.station_dist_mean import StationDistMean
from common.packets.trips_count_by_year_joined import TripsCountByYearJoined
from common.readers import WeatherReader, StationReader, TripReader, WeatherInfo, StationInfo, TripInfo
from common.utils import initialize_log


class BasicClient(ABC):
    def __init__(self, config: dict):
        self._push_addr = config["push_addr"]
        self._req_addr = config["req_addr"]
        self._cities_with_geodata = config["cities_with_geodata"]
        self._all_cities = config["cities_with_geodata"] + config["cities_without_geodata"]
        self._context = zmq.Context()

        self.__set_up_signal_handler()

    def __set_up_signal_handler(self):
        def signal_handler(sig, frame):
            logging.info("action: shutdown_client | result: in_progress")
            self._context.term()
            logging.info("action: shutdown_client | result: success")

        signal.signal(signal.SIGTERM, signal_handler)

    @staticmethod
    @abstractmethod
    def get_weather(city: str) -> Iterator[WeatherInfo]:
        pass

    @staticmethod
    @abstractmethod
    def get_stations(city: str) -> Iterator[StationInfo]:
        pass

    @staticmethod
    @abstractmethod
    def get_trips(city: str) -> Iterator[List[TripInfo]]:
        pass

    @abstractmethod
    def handle_dur_avg_out_packet(self, packet: DurAvgOut):
        pass

    @abstractmethod
    def handle_trip_count_by_year_joined_packet(self, packet: TripsCountByYearJoined):
        pass

    @abstractmethod
    def handle_station_dist_mean_packet(self, packet: StationDistMean):
        pass

    def __send_weather_data(self, socket: ST, city: str):
        for weather_info in self.get_weather(city):
            socket.send(PacketFactory.build_weather_packet(weather_info))
        socket.send(PacketFactory.build_weather_eof(city))

    def __send_stations_data(self, socket: ST, city: str):
        for station_info in self.get_stations(city):
            socket.send(PacketFactory.build_station_packet(station_info))
        socket.send(PacketFactory.build_station_eof(city))

    def __send_trips_data(self, socket: ST, city: str):
        for trip_info in self.get_trips(city):
            socket.send(PacketFactory.build_trip_packet(trip_info))
        socket.send(PacketFactory.build_trip_eof(city))

    def __send_data_from_city(self, city: str):
        logging.info(f"action: client_send_data | result: in_progress | city: {city}")
        push_socket = self._context.socket(zmq.PUSH)
        push_socket.setsockopt(zmq.LINGER, 0)
        push_socket.connect(self._push_addr)

        try:
            self.__send_weather_data(push_socket, city)
            self.__send_stations_data(push_socket, city)
            self.__send_trips_data(push_socket, city)
            logging.info(f"action: client_send_data | result: success | city: {city}")
        except zmq.ContextTerminated:
            logging.info(f"action: client_send_data | result: interrupted | city: {city}")
        except Exception as e:
            logging.error(f"action: client_send_data | result: error | city: {city} | error: {e}")
        finally:
            push_socket.close(-1)

    def __send_cities_data(self):
        threads = []
        for city in self._all_cities:
            thread = threading.Thread(target=self.__send_data_from_city, args=(city,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def __get_dur_avg_response(self, socket):
        cities_ended = []
        while len(cities_ended) < len(self._all_cities):
            socket.send(DUR_AVG_REQUEST)
            data = socket.recv()
            message = json.loads(data)
            if message["type"] == "eof":
                city = message["payload"]
                cities_ended.append(city)
            elif message["type"] == "data":
                payload = message["payload"]
                packet = DurAvgOut.decode(payload)
                self.handle_dur_avg_out_packet(packet)
            else:  # chunk
                chunk = json.loads(message["payload"])
                for msg in chunk:
                    packet = DurAvgOut.decode(msg)
                    self.handle_dur_avg_out_packet(packet)

    def __get_trip_count_response(self, socket):
        cities_ended = []
        while True:
            socket.send(TRIP_COUNT_REQUEST)
            data = socket.recv()
            message = json.loads(data)
            if message["type"] == "eof":
                city = message["payload"]
                cities_ended.append(city)
                if len(cities_ended) == len(self._all_cities):
                    break
            elif message["type"] == "data":
                payload = message["payload"]
                packet = TripsCountByYearJoined.decode(payload)
                self.handle_trip_count_by_year_joined_packet(packet)
            else:  # chunk
                chunk = json.loads(message["payload"])
                for msg in chunk:
                    packet = TripsCountByYearJoined.decode(msg)
                    self.handle_trip_count_by_year_joined_packet(packet)

    def __get_dist_mean_response(self, socket):
        cities_ended = []
        while True:
            socket.send(DIST_MEAN_REQUEST)
            data = socket.recv()
            message = json.loads(data)
            if message["type"] == "eof":
                city = message["payload"]
                cities_ended.append(city)
                if len(cities_ended) == len(self._cities_with_geodata):
                    break
            elif message["type"] == "data":
                payload = message["payload"]
                packet = StationDistMean.decode(payload)
                self.handle_station_dist_mean_packet(packet)
            else:  # chunk
                chunk = json.loads(message["payload"])
                for msg in chunk:
                    packet = StationDistMean.decode(msg)
                    self.handle_station_dist_mean_packet(packet)

    def __get_responses(self):
        req_socket = self._context.socket(zmq.REQ)
        req_socket.connect(self._req_addr)
        req_socket.setsockopt(zmq.LINGER, 0)

        try:
            self.__get_dur_avg_response(req_socket)
            self.__get_trip_count_response(req_socket)
            self.__get_dist_mean_response(req_socket)
            logging.info("action: client_get_responses | result: success")
        except zmq.ContextTerminated:
            logging.info("action: client_get_responses | result: interrupted")
        except Exception as e:
            logging.error(f"action: client_get_responses | result: error | error: {e}")
        finally:
            req_socket.close(-1)

    def __run(self):
        self.__send_cities_data()
        self.__get_responses()

    def run(self):
        thread = threading.Thread(target=self.__run)
        thread.start()
        thread.join()

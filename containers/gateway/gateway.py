import json
import logging
import os
import signal
import threading
from typing import Union, List

import zmq

from common.packet_factory import PacketFactory
from common.packets.basic_station_side_table_info import BasicStationSideTableInfo
from common.packets.eof import Eof
from common.packets.full_station_side_table_info import FullStationSideTableInfo
from common.packets.gateway_in import GatewayIn
from common.packets.weather_side_table_info import WeatherSideTableInfo
from common.rabbit_middleware import Rabbit
from common.readers import WeatherInfo, StationInfo, TripInfo
from common.utils import initialize_log, build_prefixed_hashed_queue_name, datetime_str_to_date_str

MONTREAL_OUTPUT_AMOUNT = int(os.environ["MONTREAL_OUTPUT_AMOUNT"])
TORONTO_OUTPUT_AMOUNT = int(os.environ["TORONTO_OUTPUT_AMOUNT"])
WASHINGTON_OUTPUT_AMOUNT = int(os.environ["WASHINGTON_OUTPUT_AMOUNT"])


class Gateway:
    def __init__(self, zmq_addr: str, output_amounts: dict):
        self._zmq_addr = zmq_addr
        self._output_amounts = output_amounts
        self._context = zmq.Context()
        self._rabbit = Rabbit("rabbitmq")

        self.__set_up_signal_handler()

    def __set_up_signal_handler(self):
        def signal_handler(sig, frame):
            logging.info("action: shutdown_gateway | result: in_progress")
            self._context.term()
            logging.info("action: shutdown_gateway | result: success")
            if self.sig_hand_prev is not None:
                self.sig_hand_prev(sig, frame)

        self.sig_hand_prev = signal.signal(signal.SIGTERM, signal_handler)

    def __handle_weather_packet(self, weather_info_or_city_eof: Union[WeatherInfo, str]):
        if isinstance(weather_info_or_city_eof, str):
            city_name = weather_info_or_city_eof
            self._rabbit.publish(f"{city_name}_weather", "stop".encode())
        else:
            weather_info = weather_info_or_city_eof
            data_packet = WeatherSideTableInfo(weather_info.date, weather_info.prectot).encode()
            self._rabbit.publish(f"{weather_info.city_name}_weather", data_packet)

    def __handle_station_packet(self, station_info_or_city_eof: Union[StationInfo, str]):
        if isinstance(station_info_or_city_eof, str):
            city_name = station_info_or_city_eof
            self._rabbit.publish(f"{city_name}_station", "stop".encode())
        else:
            station_info = station_info_or_city_eof
            if station_info.latitude is None or station_info.longitude is None:
                data_packet = BasicStationSideTableInfo(station_info.code, station_info.yearid,
                                                        station_info.name).encode().decode()
            else:
                data_packet = FullStationSideTableInfo(station_info.code, station_info.yearid,
                                                       station_info.name, station_info.latitude,
                                                       station_info.longitude).encode()
            self._rabbit.publish(f"{station_info.city_name}_station", data_packet)

    def __build_chunk(self, trip_infos: List[TripInfo]) -> List[str]:
        chunk = []
        for trip_info in trip_infos:
            start_date = datetime_str_to_date_str(trip_info.start_datetime)
            packet_to_send = GatewayIn(start_date, trip_info.start_station_code, trip_info.end_station_code,
                                       trip_info.duration_sec, trip_info.yearid)
            chunk.append(packet_to_send.encode().decode())
        return chunk

    def __handle_trip_packet(self, trip_info_list_or_city_eof: Union[List[TripInfo], str]):
        if isinstance(trip_info_list_or_city_eof, str):
            city_name = trip_info_list_or_city_eof
            self._rabbit.produce(f"{city_name}_gateway_in_eof_in", Eof().encode())
        else:
            trip_info_list = trip_info_list_or_city_eof
            city_name = trip_info_list[0].city_name
            first_start_date = datetime_str_to_date_str(trip_info_list[0].start_datetime)
            chunk = self.__build_chunk(trip_info_list_or_city_eof)
            chunk_packet = json.dumps({
                "type": "chunk",
                "payload": json.dumps(chunk)
            }).encode()

            queue_name = build_prefixed_hashed_queue_name(city_name, "gateway_in", first_start_date,
                                                          self._output_amounts[city_name])
            self._rabbit.produce(queue_name, chunk_packet)

    def __start(self):
        socket = self._context.socket(zmq.PULL)
        socket.setsockopt(zmq.LINGER, 0)
        socket.bind(self._zmq_addr)
        try:
            while True:
                message = bytes(socket.recv())
                PacketFactory.handle_packet(message,
                                            self.__handle_weather_packet,
                                            self.__handle_station_packet,
                                            self.__handle_trip_packet)
        except Exception as e:
            logging.info(f"action: gateway_start | status: interrupted | error: {e}")
        finally:
            socket.close()

    def start(self):
        thread = threading.Thread(target=self.__start)
        thread.start()
        thread.join()


def main():
    initialize_log(logging.INFO)
    gateway = Gateway("tcp://0.0.0.0:5555", {
        "montreal": MONTREAL_OUTPUT_AMOUNT,
        "toronto": TORONTO_OUTPUT_AMOUNT,
        "washington": WASHINGTON_OUTPUT_AMOUNT
    })
    gateway.start()


if __name__ == "__main__":
    main()

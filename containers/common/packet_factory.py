import json
import logging
from typing import List

from common.readers import WeatherInfo, StationInfo, TripInfo

DIST_MEAN_REQUEST = b'dist_mean'
TRIP_COUNT_REQUEST = b'trip_count'
DUR_AVG_REQUEST = b'dur_avg'


class PacketFactory:
    @staticmethod
    def build_weather_packet(weather_info: WeatherInfo) -> bytes:
        return json.dumps({
            "type": "weather",
            "payload": weather_info.encode().decode()
        }).encode()

    @staticmethod
    def build_weather_eof(city: str) -> bytes:
        return json.dumps({
            "type": "eof_weather",
            "payload": city
        }).encode()

    @staticmethod
    def build_station_packet(station_info: StationInfo) -> bytes:
        return json.dumps({
            "type": "station",
            "payload": station_info.encode().decode()
        }).encode()

    @staticmethod
    def build_station_eof(city: str) -> bytes:
        return json.dumps({
            "type": "eof_station",
            "payload": city
        }).encode()

    @staticmethod
    def build_trip_packet(trip_info: List[TripInfo]) -> bytes:
        return json.dumps({
            "type": "trip",
            "payload": [trip.encode().decode() for trip in trip_info]
        }).encode()

    @staticmethod
    def build_trip_eof(city: str) -> bytes:
        return json.dumps({
            "type": "eof_trip",
            "payload": city
        }).encode()

    @staticmethod
    def handle_packet(data: bytes, weather_callback, station_callback, trip_callback):
        decoded = json.loads(data.decode())
        packet_type = decoded["type"]
        payload = decoded["payload"]
        if packet_type == "weather":
            weather_callback(WeatherInfo.decode(payload.encode()))
        elif packet_type == "eof_weather":
            weather_callback(payload)
        elif packet_type == "station":
            station_callback(StationInfo.decode(payload.encode()))
        elif packet_type == "eof_station":
            station_callback(payload)
        elif packet_type == "trip":
            trip_info_list = [TripInfo.decode(trip) for trip in payload]
            trip_callback(trip_info_list)
        elif packet_type == "eof_trip":
            trip_callback(payload)
        else:
            raise ValueError(f"Unknown packet type: {packet_type}")

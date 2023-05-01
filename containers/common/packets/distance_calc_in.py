import json
from dataclasses import dataclass

from common.packets.basic_packet import BasicPacket


@dataclass
class DistanceCalcIn(BasicPacket):
    city_name: str

    start_station_name: str
    start_station_longitude: float
    start_station_latitude: float

    end_station_name: str
    end_station_longitude: float
    end_station_latitude: float

    @classmethod
    def decode(cls, data: bytes) -> "DistanceCalcIn":
        data = json.loads(data)
        city_name = data["city_name"]
        start_station_name = data["start_station_name"]
        start_station_longitude = data["start_station_longitude"]
        start_station_latitude = data["start_station_latitude"]

        end_station_name = data["end_station_name"]
        end_station_longitude = data["end_station_longitude"]
        end_station_latitude = data["end_station_latitude"]

        return DistanceCalcIn(city_name, start_station_name, start_station_longitude, start_station_latitude,
                              end_station_name, end_station_longitude, end_station_latitude)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

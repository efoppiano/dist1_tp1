import json
from dataclasses import dataclass


@dataclass
class TripsCountByYearJoined:
    city_name: str
    start_station_name: str
    trips_16: int
    trips_17: int

    @classmethod
    def decode(cls, data: bytes) -> "TripsCountByYearJoined":
        data = json.loads(data)
        city_name = data["city_name"]
        start_station_name = data["start_station_name"]
        trips_16 = data["trips_16"]
        trips_17 = data["trips_17"]
        return TripsCountByYearJoined(city_name, start_station_name, trips_16, trips_17)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

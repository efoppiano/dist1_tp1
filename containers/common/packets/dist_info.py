import json
from dataclasses import dataclass


@dataclass
class DistInfo:
    city_name: str
    start_station_name: str
    distance_km: float

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

    @classmethod
    def decode(cls, data: bytes) -> "DistInfo":
        data = json.loads(data)
        return DistInfo(data["city_name"], data["start_station_name"], float(data["distance_km"]))

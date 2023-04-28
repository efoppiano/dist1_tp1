import json
from dataclasses import dataclass


@dataclass
class StationDistMean:
    city_name: str
    start_station_name: str
    dist_mean: float

    @classmethod
    def decode(cls, data: bytes) -> "StationDistMean":
        data = json.loads(data)
        return StationDistMean(data["city_name"], data["start_station_name"], data["dist_mean"])

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

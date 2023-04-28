import json
from dataclasses import dataclass


@dataclass
class DurAvgOut:
    city_name: str
    start_date: str
    mean_duration_sec: float

    @classmethod
    def decode(cls, data: bytes) -> "DurAvgOut":
        data = json.loads(data)
        city_name = data["city_name"]
        start_date = data["start_date"]
        mean_duration_sec = data["mean_duration_sec"]
        return DurAvgOut(city_name, start_date, mean_duration_sec)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

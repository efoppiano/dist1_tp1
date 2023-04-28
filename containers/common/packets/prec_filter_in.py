import json
from dataclasses import dataclass


@dataclass
class PrecFilterIn:
    city_name: str
    start_date: str
    duration_sec: float
    prectot: float

    @classmethod
    def decode(cls, data: bytes) -> "PrecFilterIn":
        data = json.loads(data)
        city_name = data["city_name"]
        start_date = data["start_date"]
        duration_sec = data["duration_sec"]
        prectot = data["prectot"]
        return PrecFilterIn(city_name, start_date, duration_sec, prectot)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

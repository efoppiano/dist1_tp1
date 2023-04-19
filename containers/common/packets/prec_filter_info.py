import json
from datetime import datetime


class PrecFilterInfo:
    def __init__(self, start_date: datetime, duration_sec: int, prectot: float):
        self.start_date = start_date
        self.duration_sec = duration_sec
        self.prectot = prectot

    @classmethod
    def decode(cls, data: bytes) -> "PrecFilterInfo":
        data = json.loads(data)
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
        duration_sec = data["duration_sec"]
        prectot = data["prectot"]
        return PrecFilterInfo(start_date, duration_sec, prectot)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()


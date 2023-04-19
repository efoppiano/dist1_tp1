import json
from datetime import datetime


class WeatherSideTableInfo:
    def __init__(self, date: datetime, prectot: float):
        self.date = date
        self.prectot = prectot

    @classmethod
    def decode(cls, data: bytes) -> "WeatherSideTableInfo":
        data = json.loads(data)
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        prectot = data["prectot"]
        return WeatherSideTableInfo(date, prectot)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()
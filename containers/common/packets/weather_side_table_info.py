import json
from dataclasses import dataclass
import datetime

from common.utils import parse_date


@dataclass
class WeatherSideTableInfo:
    date: datetime.date
    prectot: float

    @classmethod
    def decode(cls, data: bytes) -> "WeatherSideTableInfo":
        data = json.loads(data)
        date = parse_date(data["date"])
        prectot = data["prectot"]
        return WeatherSideTableInfo(date, prectot)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

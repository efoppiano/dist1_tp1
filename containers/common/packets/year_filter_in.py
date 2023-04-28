import json
from dataclasses import dataclass


@dataclass
class YearFilterIn:
    city_name: str
    start_station_name: str
    yearid: int

    @classmethod
    def decode(cls, data: bytes) -> "YearFilterIn":
        data = json.loads(data)
        city_name = data["city_name"]
        start_station_name = data["start_station_name"]
        yearid = data["yearid"]
        return YearFilterIn(city_name, start_station_name, yearid)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

    @classmethod
    def eof(cls, city_name: str) -> bytes:
        return json.dumps({"city_name": city_name, "eof": True}).encode()

    @classmethod
    def is_eof(cls, data: bytes) -> bool:
        data = json.loads(data)
        return data.get("eof", False)

    @classmethod
    def decode_city_from_eof(cls, data: bytes) -> str:
        data = json.loads(data)
        return data["city_name"]


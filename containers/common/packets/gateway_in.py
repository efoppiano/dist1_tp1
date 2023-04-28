import json
from dataclasses import dataclass


@dataclass
class GatewayIn:
    start_date: str
    start_station_code: int
    end_station_code: int
    duration_sec: float
    yearid: int

    @classmethod
    def decode(cls, data: bytes) -> "GatewayIn":
        data = json.loads(data)
        start_date = data["start_date"]
        start_station_code = data["start_station_code"]
        end_station_code = data["end_station_code"]
        duration_sec = data["duration_sec"]
        yearid = data["yearid"]

        return GatewayIn(start_date, start_station_code, end_station_code, duration_sec, yearid)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()


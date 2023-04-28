import json
from dataclasses import dataclass

from common.packets.gateway_in import GatewayIn


@dataclass
class GatewayOut:
    start_date: str
    start_station_code: int
    end_station_code: int
    duration_sec: float
    yearid: int
    prectot: float

    @classmethod
    def decode(cls, data: bytes) -> "GatewayOut":
        data = json.loads(data)
        start_date = data["start_date"]
        start_station_code = data["start_station_code"]
        end_station_code = data["end_station_code"]
        duration_sec = data["duration_sec"]
        yearid = data["yearid"]
        prectot = data["prectot"]
        return GatewayOut(start_date, start_station_code, end_station_code, duration_sec, yearid, prectot)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

    @classmethod
    def from_gateway_in(cls, gateway_in: GatewayIn, prectot: float) -> "GatewayOut":
        return GatewayOut(gateway_in.start_date, gateway_in.start_station_code, gateway_in.end_station_code,
                          gateway_in.duration_sec, gateway_in.yearid, prectot)

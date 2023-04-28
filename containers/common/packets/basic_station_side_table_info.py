import json
from dataclasses import dataclass


@dataclass
class BasicStationSideTableInfo:
    station_code: int
    yearid: int
    station_name: str

    @classmethod
    def decode(cls, data: bytes) -> "BasicStationSideTableInfo":
        data = json.loads(data)
        station_code = data["station_code"]
        yearid = data["yearid"]
        station_name = data["station_name"]

        return BasicStationSideTableInfo(station_code, yearid, station_name)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()
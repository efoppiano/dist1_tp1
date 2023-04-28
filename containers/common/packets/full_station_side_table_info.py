import json
from dataclasses import dataclass


@dataclass
class FullStationSideTableInfo:
    station_code: int
    yearid: int
    station_name: str
    latitude: float
    longitude: float

    @classmethod
    def decode(cls, data: bytes) -> "FullStationSideTableInfo":
        data = json.loads(data)
        station_code = data["station_code"]
        yearid = data["yearid"]
        station_name = data["station_name"]
        latitude = data["latitude"]
        longitude = data["longitude"]

        return FullStationSideTableInfo(station_code, yearid, station_name, latitude, longitude)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

import json
from dataclasses import dataclass


@dataclass
class TripsCountInByYear:
    start_station_name: str
    yearid: int
    trips_count: int

    @classmethod
    def decode(cls, data: bytes) -> "TripsCountInByYear":
        data = json.loads(data)
        start_station_name = data["start_station_name"]
        yearid = data["yearid"]
        trips_count = data["trips_count"]
        return TripsCountInByYear(start_station_name, yearid, trips_count)

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

    @classmethod
    def eof(cls, yearid: int) -> bytes:
        return json.dumps({"yearid": yearid, "eof": True}).encode()

    @classmethod
    def is_eof(cls, data: bytes) -> bool:
        data = json.loads(data)
        return data.get("eof", False)

    @classmethod
    def get_yearid_from_eof(cls, data: bytes) -> int:
        data = json.loads(data)
        return data["yearid"]

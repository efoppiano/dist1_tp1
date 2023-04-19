import json
from datetime import datetime


class GatewayTripInfo:
    def __init__(self, start_date: datetime, start_station_code: int, end_station_code: int, duration_sec: int, yearid: int):
        self.start_date = start_date
        self.start_station_code = start_station_code
        self.end_station_code = end_station_code
        self.duration_sec = duration_sec
        self.yearid = yearid
        self.prectot = None

    @classmethod
    def decode(cls, data: bytes) -> "GatewayTripInfo":
        data = json.loads(data)
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
        start_station_code = data["start_station_code"]
        end_station_code = data["end_station_code"]
        duration_sec = data["duration_sec"]
        yearid = data["yearid"]
        return GatewayTripInfo(start_date, start_station_code, end_station_code, duration_sec, yearid)

    def encode(self) -> bytes:
        if self.prectot is None:
            dict_without_prectot = self.__dict__.copy()
            del dict_without_prectot["prectot"]
            return json.dumps(dict_without_prectot).encode()
        else:
            return json.dumps(self.__dict__).encode()
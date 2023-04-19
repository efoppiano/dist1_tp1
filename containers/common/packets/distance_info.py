import json


class DistanceInfo:
    def __init__(self, start_station_name: str, distance_km: float):
        self.start_station_name = start_station_name
        self.distance_km = distance_km

    def encode(self) -> bytes:
        return json.dumps(self.__dict__).encode()

    @classmethod
    def decode(cls, data: bytes) -> "DistanceInfo":
        data = json.loads(data)
        return DistanceInfo(data["start_station_name"], data["distance_km"])

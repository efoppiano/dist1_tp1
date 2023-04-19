import json


class _StationInfo:
    def __init__(self, station_name: str, station_longitude: float, station_latitude: float):
        self.station_name = station_name
        self.station_longitude = station_longitude
        self.station_latitude = station_latitude


class DistanceCalcInfo:
    def __init__(self, start_station_info: _StationInfo, end_station_info: _StationInfo):
        self.start_station_name = start_station_info.station_name
        self.start_station_longitude = start_station_info.station_longitude
        self.start_station_latitude = start_station_info.station_latitude

        self.end_station_name = end_station_info.station_name
        self.end_station_longitude = end_station_info.station_longitude
        self.end_station_latitude = end_station_info.station_latitude

    @classmethod
    def decode(cls, data: bytes) -> "DistanceCalcInfo":
        data = json.loads(data)
        start_station_name = data["start_station_name"]
        start_station_longitude = data["start_station_longitude"]
        start_station_latitude = data["start_station_latitude"]
        start_station_info = _StationInfo(start_station_name, start_station_longitude, start_station_latitude)

        end_station_name = data["end_station_name"]
        end_station_longitude = data["end_station_longitude"]
        end_station_latitude = data["end_station_latitude"]
        end_station_info = _StationInfo(end_station_name, end_station_longitude, end_station_latitude)

        return DistanceCalcInfo(start_station_info, end_station_info)

from dataclasses import dataclass

from common.packets.basic_packet import BasicPacket


@dataclass
class StationDistMean(BasicPacket):
    city_name: str
    start_station_name: str
    dist_mean: float

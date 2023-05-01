from dataclasses import dataclass

from common.packets.basic_packet import BasicPacket


@dataclass
class GatewayIn(BasicPacket):
    start_date: str
    start_station_code: int
    end_station_code: int
    duration_sec: float
    yearid: int

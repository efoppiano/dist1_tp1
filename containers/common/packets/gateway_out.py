from dataclasses import dataclass

from common.packets.basic_packet import BasicPacket


@dataclass
class GatewayOut(BasicPacket):
    start_date: str
    start_station_code: int
    end_station_code: int
    duration_sec: float
    yearid: int
    prectot: float

#!/usr/bin/env python3
import logging
from typing import Union
from haversine import haversine

from common.basic_filter import BasicFilter
from common.packets.distance_calc_info import DistanceCalcInfo
from common.packets.distance_info import DistanceInfo
from common.utils import initialize_log


class DistanceCalculator(BasicFilter):
    def handle_message(self, message: bytes) -> Union[bytes, None]:
        packet = DistanceCalcInfo.decode(message)
        logging.info("start_station_name: {}".format(packet.start_station_name))

        distance_km = self.__calculate_distance(packet.start_station_latitude, packet.start_station_longitude,
                                                packet.end_station_latitude, packet.end_station_longitude)

        logging.info("distance: {}".format(distance_km))
        return DistanceInfo(packet.start_station_name, distance_km).encode()

    @staticmethod
    def __calculate_distance(start_station_latitude: float, start_station_longitude: float,
                             end_station_latitude: float, end_station_longitude: float) -> float:
        return haversine((start_station_latitude, start_station_longitude),
                         (end_station_latitude, end_station_longitude))


def main():
    initialize_log(logging.DEBUG)
    filter = DistanceCalculator("distance_calc_in", "distance_calc_out")
    filter.start()


if __name__ == "__main__":
    main()

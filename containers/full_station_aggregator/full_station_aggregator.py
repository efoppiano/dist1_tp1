#!/usr/bin/env python3
import logging
import os
from typing import Dict, List

from common.basic_aggregator import BasicAggregator
from common.packets.distance_calc_in import DistanceCalcIn
from common.packets.eof import Eof
from common.packets.full_station_side_table_info import FullStationSideTableInfo
from common.packets.gateway_out import GatewayOut
from common.packets.prec_filter_in import PrecFilterIn
from common.packets.year_filter_in import YearFilterIn
from common.utils import initialize_log, build_prefixed_queue_name, build_eof_in_queue_name

CITY_NAME = os.environ["CITY_NAME"]
INPUT_QUEUE_SUFFIX = os.environ["INPUT_QUEUE_SUFFIX"]
PREC_FILTER_IN_QUEUE_NAME = os.environ["PREC_FILTER_IN_QUEUE_NAME"]
PREC_FILTER_AMOUNT = os.environ["PREC_FILTER_AMOUNT"]
YEAR_FILTER_IN_QUEUE_NAME = os.environ["YEAR_FILTER_IN_QUEUE_NAME"]
YEAR_FILTER_AMOUNT = os.environ["YEAR_FILTER_AMOUNT"]
DISTANCE_CALC_IN_QUEUE_NAME = os.environ["DISTANCE_CALC_IN_QUEUE_NAME"]
DISTANCE_CALC_AMOUNT = os.environ["DISTANCE_CALC_AMOUNT"]
SIDE_TABLE_QUEUE_SUFFIX = os.environ["SIDE_TABLE_QUEUE_SUFFIX"]
REPLICA_ID = os.environ["REPLICA_ID"]


class FullStationAggregator(BasicAggregator):
    def __init__(self, config: Dict[str, str]):
        self._city_name = config["city_name"]
        replica_id = int(config["replica_id"])
        side_table_queue = build_prefixed_queue_name(config["city_name"], config["side_table_queue_suffix"])
        super().__init__(self._city_name, config["input_queue_suffix"], replica_id, side_table_queue)

        self._prec_filter_in_queue_name = config["prec_filter_in_queue_name"]
        self._prec_filter_amount = int(config["prec_filter_amount"])
        self._year_filter_in_queue_name = config["year_filter_in_queue_name"]
        self._year_filter_amount = int(config["year_filter_amount"])
        self._distance_calc_in_queue_name = config["distance_calc_in_queue"]
        self._distance_calc_amount = int(config["distance_calc_amount"])
        self._stations = {}

    def handle_eof(self, message: bytes) -> Dict[str, List[bytes]]:
        eof_year_filter_in_queue = build_eof_in_queue_name(self._year_filter_in_queue_name)
        eof_prec_filter_in_queue = build_eof_in_queue_name(self._prec_filter_in_queue_name)
        eof_distance_calc_in_queue = build_eof_in_queue_name(self._distance_calc_in_queue_name)

        return {
            eof_year_filter_in_queue: [Eof(self._city_name).encode()],
            eof_prec_filter_in_queue: [Eof(self._city_name).encode()],
            eof_distance_calc_in_queue: [Eof(self._city_name).encode()],
        }

    def handle_side_table_message(self, message: bytes):
        packet = FullStationSideTableInfo.decode(message)
        station_code, yearid = packet.station_code, packet.yearid

        self._stations[(station_code, yearid)] = {
            "station_name": packet.station_name,
            "latitude": packet.latitude,
            "longitude": packet.longitude,
        }

    def __assert_station_name_exists(self, station_code: int, yearid: int):
        if (station_code, yearid) not in self._stations:
            raise ValueError(f"Station name not found for station code {station_code} and yearid {yearid}")

    def handle_message(self, message: bytes) -> Dict[str, List[bytes]]:
        packet = GatewayOut.decode(message)

        self.__assert_station_name_exists(packet.start_station_code, packet.yearid)
        self.__assert_station_name_exists(packet.end_station_code, packet.yearid)

        start_station_info = self._stations[(packet.start_station_code, packet.yearid)]
        end_station_info = self._stations[(packet.end_station_code, packet.yearid)]

        prec_filter_in_packet = PrecFilterIn(
            self._city_name, packet.start_date, packet.duration_sec, packet.prectot
        )

        year_filter_in_packet = YearFilterIn(
            self._city_name, start_station_info["station_name"], packet.yearid
        )

        distance_calc_in_packet = DistanceCalcIn(
            self._city_name,
            start_station_info["station_name"],
            start_station_info["latitude"],
            start_station_info["longitude"],
            end_station_info["station_name"],
            end_station_info["latitude"],
            end_station_info["longitude"],
        )

        return {
            self._prec_filter_in_queue_name: [prec_filter_in_packet.encode()],
            self._year_filter_in_queue_name: [year_filter_in_packet.encode()],
            self._distance_calc_in_queue_name: [distance_calc_in_packet.encode()],
        }


def main():
    initialize_log(logging.INFO)
    aggregator = FullStationAggregator({
        "city_name": CITY_NAME,
        "input_queue_suffix": INPUT_QUEUE_SUFFIX,
        "prec_filter_in_queue_name": PREC_FILTER_IN_QUEUE_NAME,
        "prec_filter_amount": PREC_FILTER_AMOUNT,
        "year_filter_in_queue_name": YEAR_FILTER_IN_QUEUE_NAME,
        "year_filter_amount": YEAR_FILTER_AMOUNT,
        "distance_calc_in_queue": "distance_calc_in",
        "distance_calc_amount": DISTANCE_CALC_AMOUNT,
        "side_table_queue_suffix": SIDE_TABLE_QUEUE_SUFFIX,
        "replica_id": REPLICA_ID,
    })
    aggregator.start()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import logging
import os
from typing import Dict, List

from common.basic_filter import BasicFilter
from common.packets.dist_info import DistInfo
from common.packets.eof import Eof
from common.packets.station_dist_mean import StationDistMean
from common.utils import initialize_log, build_hashed_queue_name, build_eof_in_queue_name

INPUT_QUEUE = os.environ["INPUT_QUEUE"]
OUTPUT_QUEUE = os.environ["OUTPUT_QUEUE"]
OUTPUT_AMOUNT = os.environ["OUTPUT_AMOUNT"]
REPLICA_ID = os.environ["REPLICA_ID"]


class DistMeanCalculator(BasicFilter):
    def __init__(self, config: Dict[str, str]):
        super().__init__(config["input_queue"], int(config["replica_id"]))

        self._output_queue = config["output_queue"]
        self._output_amount = int(config["output_amount"])

        self._buffer = {}

    def handle_eof(self, message: bytes) -> Dict[str, List[bytes]]:
        city_name = message.decode("utf-8")
        eof_output_queue = build_eof_in_queue_name(self._output_queue)
        output = {}
        self._buffer.setdefault(city_name, {})
        for start_station_name, data in self._buffer[city_name].items():
            queue = build_hashed_queue_name(self._output_queue,
                                            start_station_name,
                                            self._output_amount)
            output.setdefault(queue, [])
            output[queue].append(StationDistMean(city_name,
                                                 start_station_name,
                                                 data["mean"]).encode())

        output[eof_output_queue] = [Eof(city_name).encode()]
        return output

    def handle_message(self, message: bytes) -> Dict[str, List[bytes]]:
        packet = DistInfo.decode(message)
        city_name = packet.city_name

        self._buffer.setdefault(city_name, {})
        self._buffer[city_name].setdefault(packet.start_station_name, {"mean": 0, "count": 0})

        old_mean = self._buffer[city_name][packet.start_station_name]["mean"]
        old_count = self._buffer[city_name][packet.start_station_name]["count"]

        new_count = old_count + 1
        new_mean = (old_mean * old_count + packet.distance_km) / new_count

        logging.info(
            f"action: dist_mean_calculated | city_name: {city_name} | start_station_name: {packet.start_station_name} |"
            f" mean: {new_mean}")
        self._buffer[city_name][packet.start_station_name]["mean"] = new_mean
        self._buffer[city_name][packet.start_station_name]["count"] = new_count

        return {}


def main():
    initialize_log(logging.INFO)
    filter = DistMeanCalculator({
        "input_queue": INPUT_QUEUE,
        "output_queue": OUTPUT_QUEUE,
        "output_amount": OUTPUT_AMOUNT,
        "replica_id": REPLICA_ID
    })
    filter.start()


if __name__ == "__main__":
    main()

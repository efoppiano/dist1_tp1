#!/usr/bin/env python3
import logging
import os
from datetime import timedelta
from typing import List, Dict

from common.basic_aggregator import BasicAggregator
from common.packets.eof import Eof
from common.packets.gateway_in import GatewayIn
from common.packets.gateway_out import GatewayOut
from common.packets.weather_side_table_info import WeatherSideTableInfo
from common.utils import initialize_log, build_prefixed_queue_name, build_prefixed_hashed_queue_name, \
    build_eof_in_queue_name

CITY_NAME = os.environ["CITY_NAME"]
INPUT_QUEUE_SUFFIX = os.environ["INPUT_QUEUE_SUFFIX"]
SIDE_TABLE_QUEUE_SUFFIX = os.environ["SIDE_TABLE_QUEUE_SUFFIX"]
OUTPUT_QUEUE_SUFFIX = os.environ["OUTPUT_QUEUE_SUFFIX"]
REPLICA_ID = os.environ["REPLICA_ID"]
OUTPUT_AMOUNT = os.environ["OUTPUT_AMOUNT"]


class WeatherAggregator(BasicAggregator):

    def __init__(self, config: Dict[str, str]):
        self._city_name = config["city_name"]
        replica_id = int(config["replica_id"])
        side_table_queue = build_prefixed_queue_name(self._city_name, config["side_table_queue_suffix"])
        super().__init__(self._city_name, config["input_queue_suffix"], replica_id, side_table_queue)

        self._output_queue_suffix = config["output_queue_suffix"]
        self._output_amount = int(config["output_amount"])

        self._weather = {}

    def handle_side_table_message(self, message: bytes):
        packet = WeatherSideTableInfo.decode(message)
        yesterday = (packet.date - timedelta(days=1)).date()
        yesterday = yesterday.strftime("%Y-%m-%d")
        self._weather[yesterday] = packet.prectot

    def handle_eof(self, message: bytes) -> Dict[str, List[bytes]]:
        logging.info("Received EOF")
        output_queue = build_eof_in_queue_name(self._city_name, self._output_queue_suffix)
        return {
            output_queue: [Eof().encode()]
        }

    def handle_message(self, message: bytes) -> Dict[str, List[bytes]]:
        packet = GatewayIn.decode(message)

        if packet.start_date in self._weather:
            output_packet = GatewayOut.from_gateway_in(packet, self._weather[packet.start_date])
            output_queue = build_prefixed_hashed_queue_name(self._city_name, self._output_queue_suffix,
                                                            packet.start_date,
                                                            self._output_amount)
            return {
                output_queue: [output_packet.encode()]
            }
        else:
            raise ValueError(f"Could not find weather for {packet.start_date}. data: {self._weather}")


def main():
    initialize_log(logging.INFO)
    aggregator = WeatherAggregator({
        "city_name": CITY_NAME,
        "input_queue_suffix": INPUT_QUEUE_SUFFIX,
        "output_queue_suffix": OUTPUT_QUEUE_SUFFIX,
        "replica_id": REPLICA_ID,
        "output_amount": OUTPUT_AMOUNT,
        "side_table_queue_suffix": SIDE_TABLE_QUEUE_SUFFIX,
    })
    aggregator.start()


if __name__ == "__main__":
    main()

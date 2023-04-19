#!/usr/bin/env python3
import logging
from datetime import timedelta
from typing import Union

from common.basic_aggregator import BasicAggregator
from common.packets.gateway_trip_info import GatewayTripInfo
from common.packets.weather_side_table_info import WeatherSideTableInfo
from common.utils import initialize_log


class WeatherAggregator(BasicAggregator):
    def __init__(self, input_queue: str, output_queue: str, side_table_queue: str):
        super().__init__(input_queue, output_queue, side_table_queue)

        self._weather = {}

    def handle_side_table_message(self, message: bytes):
        packet = WeatherSideTableInfo.decode(message)
        yesterday = packet.date - timedelta(days=1)
        self._weather[yesterday] = packet.prectot

    def handle_message(self, message: bytes) -> Union[bytes, None]:
        info = GatewayTripInfo.decode(message)

        if info.start_date in self._weather:
            info.prectot = self._weather[info.start_date]
            return info.encode()
        else:
            logging.error(f"Could not find weather for {info.start_date}")


def main():
    initialize_log(logging.DEBUG)
    aggregator = WeatherAggregator("wa_gateway_trip_info", "wa_gateway_trip_info_with_weather",
                                   "wa_weather_side_table_info")
    aggregator.start()


if __name__ == "__main__":
    main()

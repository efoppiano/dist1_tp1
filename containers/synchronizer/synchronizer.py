#!/usr/bin/env python3
import logging
from dataclasses import dataclass
from typing import Dict, List

import yaml

from common.basic_synchronizer import BasicSynchronizer
from common.packets.eof import Eof
from common.utils import initialize_log


@dataclass
class SyncPoint:
    input_queue: str
    eofs_expected: int
    output_msg: bytes


class Synchronizer(BasicSynchronizer):
    def __init__(self, config: dict):
        input_queues = [eof_input for eof_input in config]
        super().__init__(input_queues)
        self._config = config
        self._eofs_received = {}
        logging.info(f"action: synchronizer_init | status: success | input_queues: {input_queues}")

    def handle_message(self, queue: str, message: bytes) -> Dict[str, List[bytes]]:
        logging.info(f"Received EOF from {queue} - {message}")
        output = {}

        self._config[queue].setdefault("by_city", False)
        if self._config[queue]["by_city"]:
            self._eofs_received.setdefault(queue, {})
            city_name = message.decode()
            self._eofs_received[queue].setdefault(city_name, 0)
            self._eofs_received[queue][city_name] += 1
            if self._eofs_received[queue][city_name] == self._config[queue]["eofs_to_wait"]:
                eof_output_queue = self._config[queue]["eof_output"]
                logging.info(f"Sending EOF to {eof_output_queue}")
                output[eof_output_queue] = [Eof().encode()]
        else:
            self._config[queue]["eofs_to_wait"] -= 1
            if self._config[queue]["eofs_to_wait"] == 0:
                eof_output_queue = self._config[queue]["eof_output"]
                logging.info(f"Sending EOF to {eof_output_queue}")
                output[eof_output_queue] = [Eof().encode()]

        return output

    """
    def handle_message(self, queue: str, message: bytes) -> Dict[str, List[bytes]]:
        logging.info(f"Received EOF from {queue} - {message}")
        output = {}
        if isinstance(self._config[queue]["eofs_to_wait"], int):
            self._config[queue]["eofs_to_wait"] -= 1
            if self._config[queue]["eofs_to_wait"] == 0:
                eof_output_queue = self._config[queue]["eof_output"]
                logging.info(f"Sending EOF to {eof_output_queue}")
                output[eof_output_queue] = [Eof().encode()]
        elif isinstance(self._config[queue]["eofs_to_wait"], dict):
            city_name = message.decode()
            self._config[queue]["eofs_to_wait"][city_name] -= 1
            if self._config[queue]["eofs_to_wait"][city_name] == 0:
                eof_output_queue = self._config[queue]["eof_output"]
                logging.info(f"Sending EOF to {eof_output_queue}")
                output[eof_output_queue] = [Eof(city_name).encode()]

        return output
    """


def main():
    initialize_log(logging.INFO)
    with open("/opt/app/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    synchronizer = Synchronizer(config)
    """
    synchronizer = Synchronizer([
        SyncPoint(
            input_queue="washington_gateway_in",
            eofs_expected=1,
            output_msg=Eof().encode()
        ),
        SyncPoint(
            input_queue="washington_gateway_out",
            eofs_expected=1,
            output_msg=Eof(city_name="wasington").encode()
        ),
        SyncPoint(
            input_queue="washington_prec_filter_in",
            eofs_expected=1,
            output_msg=Eof("washington").encode()
        ),
        SyncPoint(
            input_queue="washington_prec_filter_in",
            eofs_expected=1,
            output_msg=Eof("washington").encode()
        ),
    ])
    """
    synchronizer.start()


if __name__ == "__main__":
    main()

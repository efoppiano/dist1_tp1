import abc
import json
import logging
import os
from abc import ABC
from typing import Dict, List

from common.rabbit_middleware import Rabbit
from common.utils import build_prefixed_queue_name, build_eof_out_queue_name

RABBIT_HOST = os.environ.get("RABBIT_HOST", "rabbitmq")


class BasicAggregator(ABC):
    def __init__(self, city_name: str, input_queue_suffix: str, replica_id: int, side_table_queue: str):
        self._input_queue = build_prefixed_queue_name(city_name, input_queue_suffix, replica_id)
        self._rabbit = Rabbit(RABBIT_HOST)
        self._rabbit.declare_queue(self._input_queue)
        logging.info(
            f"Routing control packets to {build_eof_out_queue_name(city_name, input_queue_suffix)}")
        self._rabbit.route(self._input_queue, "control",
                           build_eof_out_queue_name(city_name, input_queue_suffix))
        self._rabbit.subscribe(side_table_queue, self.__on_side_table_message_callback)

    def __on_side_table_message_callback(self, msg: bytes) -> bool:
        if msg == b'stop':
            logging.info("Stopping side table consumer")
            self._rabbit.consume(self._input_queue, self.__on_stream_message_callback)
        else:
            logging.info(f"Received side table message: {msg}")
            self.handle_side_table_message(msg)

        return True

    def __on_stream_message_callback(self, msg: bytes) -> bool:
        logging.info(f"Received stream message: {msg}")
        msg = json.loads(msg)
        if msg["type"] == "eof":
            outgoing_messages = self.handle_eof(msg["payload"].encode())
        else:  # type == "data"
            outgoing_messages = self.handle_message(msg["payload"].encode())

        for (queue, messages) in outgoing_messages.items():
            for message in messages:
                message = {
                    "type": "data",
                    "payload": message.decode("utf-8")
                }
                self._rabbit.produce(queue, json.dumps(message).encode())

        return True

    @abc.abstractmethod
    def handle_message(self, message: bytes) -> Dict[str, List[bytes]]:
        pass

    @abc.abstractmethod
    def handle_eof(self, message: bytes) -> Dict[str, List[bytes]]:
        pass

    @abc.abstractmethod
    def handle_side_table_message(self, message: bytes):
        pass

    def start(self):
        self._rabbit.start()

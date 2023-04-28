import abc
import json
import logging
import os
from abc import ABC
from typing import List, Dict

from common.rabbit_middleware import Rabbit
from common.utils import build_eof_out_queue_name, build_queue_name

RABBIT_HOST = os.environ.get("RABBIT_HOST", "rabbitmq")


class BasicFilter(ABC):
    def __init__(self, input_queue_name: str, replica_id: int):
        self._input_queue = build_queue_name(input_queue_name, replica_id)
        self._rabbit = Rabbit(RABBIT_HOST)
        self._rabbit.consume(self._input_queue, self.__on_message_callback)
        self._rabbit.route(self._input_queue, "control", build_eof_out_queue_name(input_queue_name))

    def __on_message_callback(self, msg: bytes) -> bool:
        msg = json.loads(msg)
        if msg["type"] == "eof":
            outgoing_messages = self.handle_eof(msg["payload"].encode())
        else:  # type == "data"
            outgoing_messages = self.handle_message(msg["payload"].encode())

        for (queue, messages) in outgoing_messages.items():
            for message in messages:
                logging.info(f"action: filter_send_message | queue: {queue} | message: {message}")
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

    def start(self):
        self._rabbit.start()

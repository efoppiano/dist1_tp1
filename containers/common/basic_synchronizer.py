import abc
import base64
import json
import logging
import os
from abc import ABC
from typing import List, Dict

from common.rabbit_middleware import Rabbit

RABBIT_HOST = os.environ.get("RABBIT_HOST", "rabbitmq")
CHUNK_SIZE = 1024


class BasicSynchronizer(ABC):
    def __init__(self, input_queues: List[str]):
        self._input_queues = input_queues
        self._rabbit = Rabbit(RABBIT_HOST)
        for input_queue in self._input_queues:
            self._rabbit.consume(input_queue,
                                 lambda msg, input_queue=input_queue: self.__on_message_callback(input_queue, msg))

    def __handle_chunk(self, input_queue: str, chunk: List[str]) -> Dict[str, List[bytes]]:
        outgoing_messages = {}
        for message in chunk:
            responses = self.handle_message(input_queue, message.encode())
            for (queue, messages) in responses.items():
                outgoing_messages.setdefault(queue, [])
                outgoing_messages[queue] += messages
        return outgoing_messages

    def __on_message_callback(self, queue: str, msg: bytes) -> bool:
        msg = json.loads(msg)
        if msg["type"] == "eof" or msg["type"] == "data":
            msg_data = msg["payload"]
            outgoing_messages = self.handle_message(queue, msg_data.encode())
        else:  # chunk
            chunk = json.loads(msg["payload"])
            outgoing_messages = self.__handle_chunk(queue, chunk)

        for (routing_key, messages) in outgoing_messages.items():
            for message in messages:
                message_dict = {
                    "type": "eof",
                    "payload": message.decode()
                }
                self._rabbit.send_to_route("control", routing_key, json.dumps(message_dict).encode())
        return True

    @abc.abstractmethod
    def handle_message(self, queue: str, message: bytes) -> Dict[str, List[bytes]]:
        pass

    def start(self):
        self._rabbit.start()

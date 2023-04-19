import abc
from abc import ABC
from typing import Union

import pika
from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel


class BasicFilter(ABC):
    def __init__(self, input_queue: str, output_queue: str):
        self._input_queue = input_queue
        self._output_queue = output_queue

        self.__initialize_filter()

    def __initialize_filter(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        self._channel = self._connection.channel()

        self._channel.queue_declare(queue=self._input_queue, durable=True)
        self._channel.queue_declare(queue=self._output_queue, durable=True)
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(queue=self._input_queue, on_message_callback=self.__on_message_callback)

    def __on_message_callback(self, ch: BlockingChannel, method, properties: BasicProperties, body: bytes):
        outgoing_message = self.handle_message(body)

        if outgoing_message is not None:
            self._channel.basic_publish(
                exchange='',
                routing_key=self._output_queue,
                body=outgoing_message,
                properties=pika.BasicProperties(
                    delivery_mode=2
                ))

        ch.basic_ack(delivery_tag=method.delivery_tag)

    @abc.abstractmethod
    def handle_message(self, message: bytes) -> Union[bytes, None]:
        pass

    def start(self):
        self._channel.start_consuming()


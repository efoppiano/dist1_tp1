from typing import Callable, Union

import pika

from common.message_queue import MessageQueue


class Rabbit(MessageQueue):

    def __init__(self, host: str):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count=1)

        self._declared_exchanges = []
        self._declared_queues = []

    def publish(self, event: str, message: bytes):
        self.__declare_exchange(event, "fanout")
        self._channel.basic_publish(exchange=event, routing_key='', body=message)

    @staticmethod
    def __callback_wrapper(callback: Callable[[bytes], bool]):
        def wrapper(ch, method, properties, body):
            if callback(body):
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag)

        return wrapper

    def subscribe(self, event: str, callback: Callable[[bytes], bool]):
        self.__declare_exchange(event, "fanout")
        result = self._channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self._channel.queue_bind(exchange=event, queue=queue_name)
        self._channel.basic_consume(queue=queue_name,
                                    on_message_callback=self.__callback_wrapper(callback),
                                    auto_ack=False)

    def route(self, queue: str, exchange: str, routing_key: str, callback: Union[Callable[[bytes], bool], None] = None):
        self.__declare_exchange(exchange, "direct")
        self.declare_queue(queue)
        self._channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)
        if callback is not None:
            self._channel.basic_consume(queue=queue, on_message_callback=self.__callback_wrapper(callback),
                                        auto_ack=False)

    def send_to_route(self, exchange: str, routing_key: str, message: bytes):
        self.__declare_exchange(exchange, "direct")
        self._channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2
            ))

    def consume(self, queue: str, callback: Callable[[bytes], bool]):
        self.declare_queue(queue)
        self._channel.basic_consume(queue=queue, on_message_callback=self.__callback_wrapper(callback), auto_ack=False)

    def produce(self, queue: str, message: bytes):
        self.declare_queue(queue)
        self._channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2
            ))

    def start(self):
        self._channel.start_consuming()

    def declare_queue(self, queue: str):
        if queue not in self._declared_queues:
            self._channel.queue_declare(queue=queue, durable=True)
            self._declared_queues.append(queue)

    def __declare_exchange(self, exchange: str, exchange_type: str):
        if exchange not in self._declared_exchanges:
            self._channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
            self._declared_exchanges.append(exchange)

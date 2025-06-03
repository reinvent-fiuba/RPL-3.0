import logging
from typing import Annotated
from fastapi import Depends
import pika
import pika.exceptions
from rpl_activities.src.config import env

class MQSender:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            [pika.URLParameters(env.QUEUE_URL)]
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="hello", durable=True, arguments={"x-message-ttl": 3600000})

    def send_submission(self, submission_id: int, language_with_version: str):
        message = f"{submission_id} {language_with_version}"
        self.channel.basic_publish(
            exchange="",
            routing_key="hello",
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            )
        )
        logging.info(f"Sent submission to MQ: {message}")

    def close(self):
        if self.connection.is_open:
            self.connection.close()
        self.channel = None
        self.connection = None

def get_mq_sender():
    try:
        mq_sender = MQSender()
        yield mq_sender
    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Failed to connect to MQ: {e}")
    finally:
        mq_sender.close()

MQSenderDependency = Annotated[MQSender, Depends(get_mq_sender)]
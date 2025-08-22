import logging
from typing import Annotated
from fastapi import Depends
import pika
import pika.exceptions
from rpl_activities.src.config import env
from fastapi import HTTPException, status
import time

MSG_TTL = 3600000  # 1 hour in ms

class MQSender:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            [pika.URLParameters(env.QUEUE_URL)]
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="hello", durable=True, arguments={"x-message-ttl": MSG_TTL})

    def send_submission(self, submission_id: int, language_with_version: str):
        message = f"{submission_id} {language_with_version}"
        self.channel.basic_publish(
            exchange="",
            routing_key="hello",
            body=message,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )

    def close(self):
        if self.connection.is_open:
            self.connection.close()
        self.channel = None
        self.connection = None


def get_mq_sender():
    max_attempts = 5
    delay = 2
    attempt = 0
    while attempt < max_attempts:
        try:
            mq_sender = MQSender()
            yield mq_sender
            if mq_sender and mq_sender.connection.is_open:
                mq_sender.close()
            break
        except pika.exceptions.AMQPError as e:
            attempt += 1
            logging.getLogger("uvicorn.error").error(
                f"Failed to connect to MQ (attempt {attempt}): {e}"
            )
            if attempt >= max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                    detail="Message Queue service is currently unavailable. Wait a few seconds and try again."
                )
            time.sleep(delay)
        except Exception as e:
            logging.getLogger("uvicorn.error").error(
                f"An error occurred while using MQSender: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="MQ service is currently unavailable. Wait a few seconds and try again."
            )


MQSenderDependency = Annotated[MQSender, Depends(get_mq_sender)]

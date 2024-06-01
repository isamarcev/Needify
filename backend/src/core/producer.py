import json
import logging
from datetime import datetime
from enum import Enum
from typing import Type

from aiokafka import AIOKafkaProducer
from bson import ObjectId

logger = logging.getLogger("root")


class KafkaProducer:
    def __init__(self, producer_class: Type[AIOKafkaProducer], bootstrap_servers: list):
        self.producer_class = producer_class
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None

    async def publish_message(self, topic: str, message: str | list | dict):
        producer = self.producer_class(bootstrap_servers=self.bootstrap_servers)
        try:
            await producer.start()
            message_bytes = self._prepare_message(message)
            # Produce message
            result = await producer.send(topic, message_bytes)
            logger.info(f"Message {message} sent to topic {topic}")
            return result
        except Exception as e:
            logger.error(f"Error while sending message to topic {topic}: {e}")
        finally:
            await producer.stop()

    def _prepare_message(self, message):
        def replace_uuids(obj):
            if isinstance(obj, dict):
                return {key: replace_uuids(value) for key, value in obj.items()}
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, ObjectId):
                return str(obj)
            else:
                return obj

        if isinstance(message, str):
            return message.encode("utf-8")
        elif isinstance(message, dict):
            message_with_strings = replace_uuids(message)
            return json.dumps(message_with_strings).encode("utf-8")
        else:
            return json.dumps(message).encode("utf-8")

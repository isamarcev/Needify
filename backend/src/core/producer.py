import json
import logging
from abc import abstractmethod, ABC
from datetime import datetime
from enum import Enum
from typing import Type

from aiokafka import AIOKafkaProducer
from bson import ObjectId

logger = logging.getLogger("root")


class BaseProducer(ABC):
    @abstractmethod
    def publish_message(self, channel: str, message: str | list | dict):
        pass


class KafkaProducer(BaseProducer):
    def __init__(self, producer_class: Type[AIOKafkaProducer], bootstrap_servers: list):
        self.producer = producer_class(bootstrap_servers=bootstrap_servers)

    async def publish_message(self, channel: str, message: str | list | dict):
        try:
            logging.info(f"Sending message to channel {channel} with message: {message}")
            await self.producer.start()
            message_bytes = self._prepare_message(message)
            await self.producer.send(channel, message_bytes)
            logging.warning(f"Message sent to channel {channel}")
        except Exception as e:
            logging.error(f"Error while sending message to channel {channel}: {e}")
        finally:
            await self.producer.stop()

    @staticmethod
    def _prepare_message(message):
        def convert_obj(obj):
            if isinstance(obj, dict):
                return {key: convert_obj(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_obj(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, Enum):
                return obj.value
            else:
                return obj

        if isinstance(message, str):
            return message.encode("utf-8")
        else:
            message_with_converted_objects = convert_obj(message)
            return json.dumps(message_with_converted_objects).encode("utf-8")

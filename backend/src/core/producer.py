import json
from datetime import datetime
from enum import Enum
from typing import Type

from aiokafka import AIOKafkaProducer
from bson import ObjectId


class KafkaProducer:
    def __init__(self, producer_class: Type[AIOKafkaProducer], bootstrap_servers: list):
        self.producer_class = producer_class
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None

    async def start(self):
        producer = self.producer_class(bootstrap_servers=self.bootstrap_servers)
        await producer.start()
        return producer

    async def stop(self, producer):
        await producer.stop()

    async def publish_message(self, topic: str, message: str | list | dict):
        producer = await self.start()
        try:
            message_bytes = self._prepare_message(message)
            # Produce message
            result = await producer.send(topic, message_bytes)
            print("Message sent", result)
            return result
        finally:
            await self.stop(producer)

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

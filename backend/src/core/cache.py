from abc import ABC, abstractmethod

from aioredis import Redis

from src.core.database import redis_database


class BaseCacheDatabase(ABC):

    @abstractmethod
    async def get_last_scanned_block(self, *args, **kwargs):
        pass

    @abstractmethod
    async def set_last_scanned_block(self, *args, **kwargs):
        pass

class RedisCacheDatabase(BaseCacheDatabase):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_last_scanned_block(self, masterchain: int = 0):
        result = await self.redis.get(f"last_scanned_block_{masterchain}")
        return int(result) if result else None

    async def set_last_scanned_block(self, block_number: int, masterchain: int = 0):
        await self.redis.set(f"last_scanned_block_{masterchain}", block_number)
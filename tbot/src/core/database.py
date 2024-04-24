import aioredis
from aiogram.fsm.storage.redis import RedisStorage

from src.core.config import env_config

REDIS_STORAGE = aioredis.from_url(env_config.telegram.REDIS_URL)  # for future use statestorage

redis_storage = RedisStorage(REDIS_STORAGE)

from pymongo import IndexModel, ASCENDING
from dependency_injector.providers import ThreadLocalSingleton
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import config
from aioredis import from_url

async_mongo = ThreadMongoSingleton(
    config.MONGO_DB_URL, config.MONGO_DB_NAME
)

redis_database = ThreadLocalSingleton(from_url, config.REDIS_URL).provided


async def setup_database(mongo_db):
    telegram_id = IndexModel([("telegram_id", ASCENDING)], unique=True)
    await mongo_db().users.create_indexes([telegram_id])
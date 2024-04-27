from pymongo import IndexModel, ASCENDING

from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import config

async_mongo = ThreadMongoSingleton(
    config.MONGO_DB_URL, config.MONGO_DB_NAME
)


async def setup_database():
    telegram_id = IndexModel([("telegram_id", ASCENDING)], unique=True)
    await async_mongo().users.create_indexes([telegram_id])
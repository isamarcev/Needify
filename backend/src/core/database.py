import logging

from aioredis import from_url
from dependency_injector.providers import ThreadLocalSingleton
from pymongo import ASCENDING, IndexModel
from redis.asyncio import Redis

from src.apps.currency.jetton_metadata import NEED_JETTON_METADATA, USDT_JETTON_METADATA
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import config

async_mongo = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
redis_database = ThreadLocalSingleton(from_url, config.REDIS_URL).provided

USDT_CURRENCY = {
    "name": USDT_JETTON_METADATA["name"],
    "symbol": USDT_JETTON_METADATA["symbol"],
    "decimals": USDT_JETTON_METADATA["decimals"],
    "address": USDT_JETTON_METADATA["address"],
    "description": USDT_JETTON_METADATA["description"],
    "image": USDT_JETTON_METADATA["image"],
    "is_active": True,
}


async def insert_default_currency():
    redis = Redis.from_url(config.REDIS_URL)
    await redis.set("jetton:usdt:address", USDT_JETTON_METADATA["address"])
    test = await redis.get("jetton:usdt:address")
    logging.info(f"Test redis: {test}")
    # USDT CURRENCY
    exist = await async_mongo().currency.find_one({"address": USDT_CURRENCY["address"]})
    if not exist:
        await async_mongo().currency.insert_one(USDT_CURRENCY)
    # NATIVE CURRENCY
    if not await async_mongo().currency.find_one({"address": NEED_JETTON_METADATA["address"]}):
        NEED_JETTON_METADATA.update({"is_active": True})
        await async_mongo().currency.insert_one(NEED_JETTON_METADATA)


async def setup_database(mongo_db):
    telegram_id = IndexModel([("telegram_id", ASCENDING)], unique=True)
    await mongo_db().users.create_indexes([telegram_id])

    await insert_default_currency()

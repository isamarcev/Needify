from aioredis import from_url
from dependency_injector.providers import ThreadLocalSingleton
from pymongo import ASCENDING, IndexModel

from src.apps.currency.custom_minter import jUSDT_content
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import config

async_mongo = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
redis_database = ThreadLocalSingleton(from_url, config.REDIS_URL).provided


async def insert_default_currency():
    USDT_CURRENCY = {
        "name": jUSDT_content["name"],
        "symbol": jUSDT_content["symbol"],
        "decimals": jUSDT_content["decimals"],
        "jetton_master_address": config.JETTON_USDT_ADDRESS,
        "is_active": True,
    }
    if not await async_mongo().currency.find_one(
        {"jetton_master_address": USDT_CURRENCY["jetton_master_address"]}
    ):
        await async_mongo().currency.insert_one(USDT_CURRENCY)

    # NATIVE CURRENCY
    NEED_CURRENCY = {
        "name": "Need",
        "symbol": "NEED",
        "decimals": 9,
        "jetton_master_address": config.NATIVE_MASTER_ADDRESS,
        "is_active": True,
    }
    if not await async_mongo().currency.find_one(
        {"jetton_master_address": NEED_CURRENCY["jetton_master_address"]}
    ):
        await async_mongo().currency.insert_one(NEED_CURRENCY)

    # await async_mongo().currency.insert_one(USDT_CURRENCY)


async def setup_database(mongo_db):
    telegram_id = IndexModel([("telegram_id", ASCENDING)], unique=True)
    await mongo_db().users.create_indexes([telegram_id])

    await insert_default_currency()

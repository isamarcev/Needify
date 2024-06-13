import asyncio

import pytest
from pymongo import MongoClient
from pytoniq import LiteClient

from src.apps.users.schemas import CreateUserSchema, UserWeb3WalletSchema
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import config
from src.core.database import setup_database
from src.core.dependencies import CoreContainer
from tests.integration.datasets.users import POSTER


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.
    :return: backend name
    """
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class MockMessageHub:
    async def consume(self):
        pass


class MockProducer:
    async def publish_message(self, topic, value):
        pass


@pytest.fixture(scope="function")
def core_container(event_loop):
    container = CoreContainer()
    config.MONGO_DB_NAME = "TEST_DATABASE_NAME"
    container.message_hub.override(MockMessageHub())
    container.producer.override(MockProducer())
    loop = asyncio.get_event_loop()
    async_mongo_test = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
    container.async_mongo.override(async_mongo_test)
    loop.run_until_complete(setup_database(async_mongo_test))
    # asyncio.run_coroutine_threadsafe(container.user_manager().setup_database())
    lite_client: LiteClient = container.lite_client()
    loop.run_until_complete(lite_client.connect())
    yield container
    # Drop test database
    sync_mongo = MongoClient(config.MONGO_DB_URL)
    sync_mongo.drop_database("TEST_DATABASE_NAME")
    loop.run_until_complete(lite_client.close())


# @pytest.fixture(scope="function", autouse=True)
# async def clean_database():
#     # Ensure the database is clean before each test
#     async_mongo_test = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
#     await async_mongo_test.drop_database()
#     await async_mongo_test.create_database()


@pytest.fixture(scope="function", autouse=True)
async def create_poster(core_container):
    user_manager = core_container.user_container.user_manager()
    await user_manager.create_user(CreateUserSchema(**POSTER))
    user = await user_manager.get_user_by_telegram_id(POSTER["telegram_id"])
    assert user.telegram_id == POSTER["telegram_id"]
    await user_manager.add_wallet(
        user.telegram_id, UserWeb3WalletSchema(address=POSTER["web3_wallet"])
    )
    print(user)

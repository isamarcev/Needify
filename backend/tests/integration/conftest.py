import asyncio

import pytest
from pymongo import MongoClient

from src.apps.users.dependencies import UserContainer
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import config
from src.core.database import setup_database
from src.core.dependencies import CoreContainer


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.
    :return: backend name
    """
    return "asyncio"


@pytest.fixture(scope="session")
def user_container():
    container = UserContainer()
    config.MONGO_DB_NAME = "TEST_DATABASE_NAME"
    container.config.from_pydantic(settings=config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(container.user_manager().setup_database())
    # asyncio.run_coroutine_threadsafe(container.user_manager().setup_database())
    yield container

    # Drop test database
    sync_mongo = MongoClient(config.MONGO_DB_URL)
    sync_mongo.drop_database("TEST_DATABASE_NAME")


@pytest.fixture(scope="session")
def core_container():
    container = CoreContainer()
    config.MONGO_DB_NAME = "TEST_DATABASE_NAME"
    loop = asyncio.get_event_loop()
    async_mongo_test = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
    loop.run_until_complete(setup_database(async_mongo_test))
    # asyncio.run_coroutine_threadsafe(container.user_manager().setup_database())
    yield container

    # Drop test database
    sync_mongo = MongoClient(config.MONGO_DB_URL)
    sync_mongo.drop_database("TEST_DATABASE_NAME")


# @pytest.fixture(scope="session")
# def user_manager():
#     async_mongo = ThreadMongoSingleton(
#         config.MONGO_DB_URL, "TEST_DATABASE_NAME"
#     )
#     user_database = MongoDBUserRepository(mongo_client=async_mongo, collection_name="users")
#     yield UserManager(user_database)
#     def drop_database():
#         sync_mongo = MongoClient(config.MONGO_DB_URL)
#         sync_mongo.drop_database("TEST_DATABASE_NAME")
#     drop_database()

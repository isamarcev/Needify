from dependency_injector import containers, providers

from src.apps.users.manager import UserManager
from src.apps.users.database import MongoDBUserRepository
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig


class UserContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.users.router",
        ],
    )

    async_mongo = providers.Factory(
        ThreadMongoSingleton,
        config.MONGO_DB_URL,
        config.MONGO_DB_NAME
    )

    user_database = providers.Factory(
        MongoDBUserRepository,
        mongo_client=async_mongo,
        collection_name="users"
    )

    user_manager = providers.Factory(
        UserManager,
        user_repository=user_database)




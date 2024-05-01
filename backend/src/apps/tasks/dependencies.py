from dependency_injector import containers, providers

from src.apps.tasks.manager import TaskManager
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.core.repository import BaseMongoRepository


class TaskContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.tasks.router",
        ],
    )

    category_manager = providers.Provider()
    wallet_manager = providers.Provider()

    async_mongo = providers.Factory(
        ThreadMongoSingleton,
        config.MONGO_DB_URL,
        config.MONGO_DB_NAME
    )

    task_database = providers.Factory(
        BaseMongoRepository,
        mongo_client=async_mongo,
        collection_name="tasks"
    )

    task_manager = providers.Factory(
        TaskManager,
        task_repository=task_database,
        category_manager=category_manager,
        wallet_manager=wallet_manager
    )

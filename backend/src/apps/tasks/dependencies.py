from dependency_injector import containers, providers

from src.apps.tasks.manager import TaskManager
from src.core.config import BaseConfig
from src.core.repository import BaseMongoRepository


class TaskContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.tasks.router",
        ],
    )
    category_manager = providers.Dependency()
    wallet_manager = providers.Dependency()
    currency_manager = providers.Dependency()
    user_manager = providers.Dependency()
    async_mongo = providers.Dependency()

    task_database = providers.Factory(
        BaseMongoRepository, mongo_client=async_mongo, collection_name="tasks"
    )

    task_manager = providers.Factory(
        TaskManager,
        task_repository=task_database,
        category_manager=category_manager,
        wallet_manager=wallet_manager,
        currency_manager=currency_manager,
        user_manager=user_manager,
    )

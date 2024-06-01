from dependency_injector import containers, providers

from src.apps.category.manager import CategoryManager
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.core.repository import BaseMongoRepository


class CategoryContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.category.routes",
        ],
    )

    async_mongo = providers.Singleton(
        ThreadMongoSingleton, config.MONGO_DB_URL, config.MONGO_DB_NAME
    )

    category_database = providers.Singleton(
        BaseMongoRepository, mongo_client=async_mongo, collection_name="categories"
    )

    category_manager = providers.Singleton(
        CategoryManager,
        repository=category_database,
    )

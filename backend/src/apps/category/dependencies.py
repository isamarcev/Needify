from src.apps.category.manager import CategoryManager
from src.core.database import async_mongo
from src.core.repository import BaseMongoRepository


# async def get_category_repository():
#     return BaseMongoRepository(
#         async_mongo,
#         collection_name="categories"
#     )


# async def get_category_manager():
#     return CategoryManager(
#         repository=await get_category_repository()
#     )


from dependency_injector import containers, providers

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

    async_mongo = providers.Factory(
        ThreadMongoSingleton,
        config.MONGO_DB_URL,
        config.MONGO_DB_NAME
    )

    category_database = providers.Factory(
        BaseMongoRepository,
        mongo_client=async_mongo,
        collection_name="categories"
    )

    category_manager = providers.Factory(
        CategoryManager,
        repository=category_database,
    )

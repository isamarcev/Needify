from src.apps.category.manager import CategoryManager
from src.core.database import async_mongo
from src.core.repository import BaseMongoRepository


async def get_category_repository():
    return BaseMongoRepository(
        async_mongo,
        collection_name="categories"
    )


async def get_category_manager():
    return CategoryManager(
        repository=await get_category_repository()
    )
import logging

from src.apps.category.examples import categories
from src.apps.category.exceptions import CategoryNotFoundException
from src.apps.category.shema import CategorySchema
from src.apps.utils.exceptions import JsonHTTPException
from src.core.repository import BaseMongoRepository

logger = logging.getLogger("root")


class CategoryManager:
    def __init__(self, repository: BaseMongoRepository):
        self.repository = repository

    async def get(
        self, category_title: str, raise_if_not_exist: bool = True
    ) -> CategorySchema | None:
        category = await self.repository.get_by_filter({"title": category_title})
        logger.info(f"Category {category_title} found: {category}")
        if category is None and raise_if_not_exist is True:
            raise CategoryNotFoundException(f"Category {category_title} not found")
        return CategorySchema(**category) if category else None

    async def get_list(self) -> list[CategorySchema]:
        return [CategorySchema(**category) for category in await self.repository.get_list()]

    async def create(self, category: CategorySchema) -> CategorySchema:
        if await self.get(category.title, raise_if_not_exist=False):
            raise JsonHTTPException(
                status_code=400,
                error_description=f"Category {category.title} already exists",
                error_name="ALREADY_EXISTS",
            )
        result = await self.repository.create(category.dict())
        return CategorySchema(**result)

    async def create_categories(self, categories: list[CategorySchema]):
        categories_to_response = []
        for category in categories:
            if await self.get(category.title, raise_if_not_exist=False):
                logger.info(f"Category {category.title} already exists")
                categories.remove(category)
                categories_to_response.append(category)
            else:
                result = await self.create(category)
                categories_to_response.append(result)
        return categories_to_response

    async def on_startup(self):
        for category in categories:
            if not await self.get(category["title"], raise_if_not_exist=False):
                await self.create(CategorySchema(**category))
        logger.info("Categories checked created")

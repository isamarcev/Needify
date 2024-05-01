from src.apps.category.shema import CategorySchema
from src.core.repository import BaseMongoRepository


class CategoryManager:
    def __init__(self, repository: BaseMongoRepository):
        self.repository = repository

    async def get(self, category_title: str) -> CategorySchema | None:
        category = await self.repository.get_by_filter({"title": category_title})
        return CategorySchema(**category) if category else None

    async def get_list(self) -> list[CategorySchema]:
        return [CategorySchema(**category) for category in await self.repository.get_list()]

    async def create(self, category: CategorySchema) -> CategorySchema:
        if await self.get(category.title):
            raise ValueError(f"Category {category.title} already exists")
        result = await self.repository.create(category.dict())
        return CategorySchema(**result)

    async def create_categories(self, categories: list[CategorySchema]):
        categories_to_response = []
        for category in categories:
            if await self.get(category.title):
                categories.remove(category)
                categories_to_response.append(category)
            else:
                result = await self.create(category)
                categories_to_response.append(result)
        return categories_to_response

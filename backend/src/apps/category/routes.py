from fastapi import APIRouter, Depends

from src.apps.category.dependencies import get_category_manager
from src.apps.category.manager import CategoryManager
from src.apps.category.shema import CategorySchema

category_router = APIRouter()


@category_router.get("/", response_model=list[CategorySchema])
async def get_categories(
        category_manager: CategoryManager = Depends(get_category_manager)
):
    return await category_manager.get_list()


@category_router.post("/", response_model=list[CategorySchema])
async def create_categories(
        categories: list[CategorySchema],
        category_manager: CategoryManager = Depends(get_category_manager)
):
    return await category_manager.create_categories(categories)


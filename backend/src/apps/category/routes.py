from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.category.dependencies import CategoryContainer
from src.apps.category.manager import CategoryManager
from src.apps.category.shema import CategorySchema

category_router = APIRouter()


@category_router.get("", response_model=list[CategorySchema])
@inject
async def get_categories(
    category_manager: CategoryManager = Depends(Provide[CategoryContainer.category_manager]),
):
    return await category_manager.get_list()


# @category_router.post("", response_model=list[CategorySchema])
# @inject
# async def create_categories(
#     categories: list[CategorySchema],
#     category_manager: CategoryManager = Depends(Provide[CategoryContainer.category_manager]),
# ):
#     return await category_manager.create_categories(categories)

from src.apps.category.dependencies import get_category_manager
from src.apps.tasks.manager import TaskManager
from src.apps.wallets.dependencies import get_wallet_manager
from src.core.repository import BaseMongoRepository
from src.core.database import async_mongo


async def get_task_repo():
    return BaseMongoRepository(
        mongo_client=async_mongo,
        collection_name="tasks"
    )


async def get_task_manager():
    category_manager = await get_category_manager()
    task_repo = await get_task_repo()
    return TaskManager(
        task_repo=task_repo,
        category_manager=category_manager,
        wallet_manager=await get_wallet_manager()
    )
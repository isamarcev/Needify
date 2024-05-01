from abc import ABC
import random

from dependency_injector.wiring import Provide, inject

from src.apps.category.dependencies import CategoryContainer
from src.apps.category.exceptions import CategoryNotFoundException
from src.apps.category.manager import CategoryManager
from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.exceptions import TaskNotFoundJsonException, TaskValidationJsonException
from src.apps.tasks.rules import ChangeStatusTaskRule
from src.apps.tasks.schemas import TaskSchema, PreCreateTaskSchema, UpdateStatusTaskSchema, \
    CreateTaskSchema, UserHistoryResponseSchema
from src.apps.wallets.manager import WalletManager
from src.core.repository import BaseMongoRepository


class BaseTaskManager(ABC):

    async def get_tasks(self):
        raise NotImplementedError()

    async def get_task(self, task_id: str):
        raise NotImplementedError()

    async def create_task(self, *args, **kwargs):
        raise NotImplementedError()

    async def update_task(self, *args, **kwargs):
        raise NotImplementedError()

    async def delete_task(self, *args, **kwargs):
        raise NotImplementedError()


class TaskManager(BaseTaskManager):

    def __init__(self,
                 task_repository: BaseMongoRepository,
                 category_manager: CategoryManager,
                 wallet_manager: WalletManager,
                 ):
        self.repository = task_repository
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.publisher = None

    @inject
    async def get_tasks(self, category: str = None) -> list[TaskSchema]:
        if category and not await self.category_manager.get(category_title=category):
            raise CategoryNotFoundException()
        if category:
            return await self.repository.get_list({"category": category})
        return await self.repository.get_list()

    async def get_by_task_id(self, task_id: int) -> TaskSchema | None:
        result = await self.repository.get_by_filter({"task_id": task_id})
        return TaskSchema(**result) if result else None

    async def get_task(self, obj_id: str):
        return await self.repository.get(obj_id)

    @staticmethod
    def task_id_generator():
        return random.randint(1000000, 1000000000)

    async def create_task(self, data_to_create: PreCreateTaskSchema) -> TaskSchema:
        if not await self.category_manager.get(data_to_create.category):
            raise CategoryNotFoundException()
        data_to_insert = data_to_create.dict()
        task_id = self.task_id_generator()
        deposit_wallet = await self.wallet_manager.create_deposit_wallet_for_task(
            task_id=task_id
        )
        data_to_insert["task_id"] = task_id
        data_to_insert["task_deposit_address"] = deposit_wallet.address
        task_for_creating = CreateTaskSchema(**data_to_insert)
        created_task = await self.repository.create(task_for_creating.dict())
        return TaskSchema(**created_task)

    async def update_task(self, task_id: int, data_to_update: dict) -> TaskSchema | None:
        task = await self.get_by_task_id(task_id)
        if not task:
            raise TaskNotFoundJsonException(task_id)
        result = await self.repository.update(task["_id"], data_to_update)
        return TaskSchema(**result) if result else None

    async def update_task_status(self, task_id: int, data_to_update: UpdateStatusTaskSchema):
        task = await self.get_by_task_id(task_id)
        if not task:
            raise TaskNotFoundJsonException(task_id)

        try:
            is_broken = ChangeStatusTaskRule(
                task, data_to_update.status, data_to_update.action_by_user_id
            ).is_broken()
            if is_broken:
                raise ValueError("Rule is broken")
        except ValueError as e:
            raise TaskValidationJsonException(str(e))

        updated_task: TaskSchema = await self.update_task(task_id, {
            "status": data_to_update.status
        })
        match updated_task.status:
            case TaskStatusEnum.CANCELLED:
                # need to return money to customer
                pass
            case TaskStatusEnum.CONFIRMED:
                # need to send money to doer wallet
                pass
        return updated_task

    async def delete_task(self, task_id: str):
        return await self.repository.delete(task_id)

    async def get_user_tasks(self, user_id: int) -> UserHistoryResponseSchema:
        published_tasks = await self.repository.get_list(
            {
                "customer_id": user_id,
                # "status": {"$in": TaskStatusEnum.customer_active_statuses()}
             }
        )
        picked_up_tasks = await self.repository.get_list(
            {
                "doer_id": user_id,
                # "status": {"$in": TaskStatusEnum.doer_active_statuses()}
             }
        )
        completed_tasks = await self.repository.get_list(
            {
                "doer_id": user_id,
                # "status": {"$in": TaskStatusEnum.done_statuses()}
             }
        )
        response = UserHistoryResponseSchema(
            published_tasks=published_tasks,
            picked_up_tasks=picked_up_tasks,
            completed_tasks=completed_tasks
        )
        return response

import logging
import random

from pytoniq_core import Address

from src.apps.category.exceptions import CategoryNotFoundException
from src.apps.category.manager import CategoryManager
from src.apps.currency.manager import CurrencyManager
from src.apps.currency.schemas import CurrencySchema
from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.exceptions import TaskNotFoundJsonException, TaskValidationJsonException
from src.apps.tasks.rules import ChangeStatusTaskRule
from src.apps.tasks.schemas import (
    CreateTaskSchema,
    PreCreateTaskSchema,
    TaskSchema,
    UpdateStatusTaskSchema,
    UserHistoryResponseSchema,
)
from src.apps.users.manager import UserManager
from src.apps.utils.exceptions import JsonHTTPException
from src.apps.wallets.manager import WalletManager
from src.core.config import config
from src.core.repository import BaseMongoRepository

logger = logging.getLogger("root")


class TaskManager:
    def __init__(
        self,
        task_repository: BaseMongoRepository,
        category_manager: CategoryManager,
        wallet_manager: WalletManager,
        currency_manager: CurrencyManager,
        user_manager: UserManager,
    ):
        self.repository = task_repository
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.currency_manager = currency_manager
        self.user_manager = user_manager
        self.publisher = None

    async def get_tasks(
        self, category: str | None = None, status: TaskStatusEnum | None = None
    ) -> list[TaskSchema]:
        if category and not await self.category_manager.get(category_title=category):
            raise CategoryNotFoundException()
        filter_ = {}
        if category:
            filter_["category"] = category
        if status:
            filter_["status"] = status
        result = await self.repository.get_list(by_filter=filter_)
        return [TaskSchema(**task) for task in result]

    async def get_by_task_id(self, task_id: int) -> TaskSchema | None:
        result = await self.repository.get_by_filter({"task_id": task_id})
        return TaskSchema(**result) if result else None

    async def get_task(self, task_id: int, raise_if_not_found: bool = True) -> TaskSchema | None:
        result = await self.repository.get_by_filter({"task_id": task_id})
        if not result and raise_if_not_found:
            raise TaskNotFoundJsonException(task_id)
        return TaskSchema(**result) if result else None

    @staticmethod
    def task_id_generator():
        return random.randint(1000000, 1000000000)

    async def check_poster_balance_for_deploy(
        self,
        poster_address: str,
        task_price: float,
        task_currency: CurrencySchema,
        native_currency: CurrencySchema,
    ):
        task_price_with_decimal = int(task_price * 10**task_currency.decimals)
        native_price_with_decimal = int(
            config.NATIVE_CURRENCY_PRICE_TO_DEPLOY * 10**native_currency.decimals
        )
        # TODO NEED TO CHECK TON BALANCE
        if not all(
            [
                await self.currency_manager.is_enough_balance(
                    task_currency, poster_address, task_price_with_decimal
                ),
                await self.currency_manager.is_enough_balance(
                    native_currency, poster_address, native_price_with_decimal
                ),
            ]
        ):
            raise TaskValidationJsonException(
                f"User wallet {poster_address} has not "
                f"enough balance for transfer {task_price} {task_currency.symbol}"
            )
        else:
            logger.info(
                f"User wallet {poster_address} has enough balance"
                f" for transfer {task_price} {task_currency.symbol}"
            )

    async def create_task(self, data_to_create: PreCreateTaskSchema) -> TaskSchema:
        poster = await self.user_manager.get_user_by_telegram_id(data_to_create.poster_id)
        if not poster.web3_wallet:
            raise JsonHTTPException(
                status_code=400,
                error_description="User has no wallet",
                error_name="BAD_REQUEST",
            )
        # await self.category_manager.get(data_to_create.category)
        similar_task = await self.repository.get_by_filter(
            {
                "title": data_to_create.title,
                "poster_id": data_to_create.poster_id,
                "price": data_to_create.price,
            }
        )
        if similar_task:
            raise TaskValidationJsonException(
                "Task with same title and price already exists. Check your tasks."
            )
        native_currency = await self.currency_manager.get_native_currency()
        task_currency: CurrencySchema = await self.currency_manager.get(data_to_create.currency)
        if not task_currency:
            logging.error(f"Currency {data_to_create.currency} not found")
            raise TaskValidationJsonException(f"Currency {data_to_create.currency} not found")

        # Check poster balance
        poster_web3_address = poster.web3_wallet.address
        await self.check_poster_balance_for_deploy(
            poster_web3_address, data_to_create.price, task_currency, native_currency
        )
        data_to_insert = data_to_create.dict()
        task_id = self.task_id_generator()
        data_to_insert["task_id"] = task_id
        data_to_insert["native_currency"] = native_currency.symbol
        data_to_insert["poster_address"] = poster.web3_wallet.address
        task_for_creating = CreateTaskSchema(**data_to_insert)
        created_task = await self.repository.create(task_for_creating.dict())
        return TaskSchema(**created_task)

    async def update_task(self, task_id: int, data_to_update: dict) -> TaskSchema | None:
        task = await self.get_by_task_id(task_id)
        if not task:
            raise TaskNotFoundJsonException(task_id)
        task = await self.repository.get_by_filter({"task_id": task_id})
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
            raise TaskValidationJsonException(str(e)) from e

        updated_task: TaskSchema = await self.update_task(
            task_id, {"status": data_to_update.status}
        )
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

    async def get_task_by_job_offer_address(self, job_offer_address: Address) -> TaskSchema | None:
        tasks = await self.get_tasks()
        for task in tasks:
            if task.job_offer is not None:
                job_offer_address_task = task.job_offer.job_offer_address
                if job_offer_address_task == job_offer_address.to_str(False):
                    return task
        result = await self.repository.get_by_filter(
            {"job_offer.job_offer_address": job_offer_address.to_str()}
        )
        return TaskSchema(**result) if result else None

    async def get_user_tasks(self, user_id: int) -> UserHistoryResponseSchema:
        published_tasks = await self.repository.get_list(
            {
                "poster_id": user_id,
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
            completed_tasks=completed_tasks,
        )
        return response

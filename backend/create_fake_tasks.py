import asyncio
import random
from datetime import datetime, timedelta

from faker import Faker

from src.apps.category.examples import categories
from src.apps.currency.jetton_metadata import NEED_JETTON_METADATA
from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.schemas import JobOfferSchema, TaskSchema
from src.apps.users.dependencies import MongoDBUserRepository
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.core.repository import BaseMongoRepository

NUMBER_OF_FAKE_TASKS = 10


async def main():
    config = BaseConfig()
    async_mongo = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
    tasks_repository = BaseMongoRepository(mongo_client=async_mongo, collection_name="taskss")
    users_repository = MongoDBUserRepository(
        config.MONGO_DB_URL, config.MONGO_DB_NAME, collection_name="users"
    )
    users = await users_repository.get_users()
    fake = Faker()
    statuses = [status.value for status in TaskStatusEnum]
    for user in users:
        user_id = user["telegram_id"]
        for status in statuses:
            task = TaskSchema(
                task_id=random.randint(
                    1000000, 1000000000
                ),  # Заменить на логику генерации уникального ID
                title=fake.text(random.randint(25, 100)),
                description=fake.text(1000),
                category=random.choice(categories)["title"],
                images=[
                    "https://incrypted.com/wp-content/uploads/2022/08/ton-100.jpg",
                    "https://pintu-academy.pintukripto.com/wp-content/uploads/2023/12/Ton.png",
                ],
                price=random.randint(50, 555),
                currency="USDT",
                status=status,
                poster_id=user_id,
                poster_address=user.get("web3_address", {}).get("address")
                if user.get("web3_address", {}).get("address")
                else "",
                deadline=datetime.now() + timedelta(days=7),
                created_at=datetime.now(),
            )

            if status not in [
                TaskStatusEnum.PRE_CREATED.value,
                TaskStatusEnum.PRE_DEPLOYING.value,
                TaskStatusEnum.DEPLOYING.value,
            ]:
                doers = await users_repository.get_users()
                doer_address = ""
                for doer in doers:
                    if (
                        doer["telegram_id"] != user_id
                        and doer.get("web3_address", {}).get("address") is not None
                        and doer.get("web3_address").get("address")
                        != user.get("web3_address", {}).get("address")
                    ):
                        doer_address = doer["web3_address"]
                        break
                job_offer = {
                    "job_offer_address": "Job offer address",
                    "jetton_master_address": "Jetton master address",
                    "jetton_native_address": NEED_JETTON_METADATA["address"],
                    "state": "Some state",
                    "owner": "Some owner",
                    "vacancies": [{"doer": doer_address, "telegram_id": 1, "is_chosen": False}],
                }

                if status in [
                    TaskStatusEnum.IN_PROGRESS.value,
                    TaskStatusEnum.COMPLETED.value,
                    TaskStatusEnum.CONFIRMED.value,
                    TaskStatusEnum.FINISHED.value,
                ]:
                    job_offer["doer"] = "Some doer"

                task.job_offer = JobOfferSchema(**job_offer)

            await tasks_repository.create(task.dict(by_alias=True))
            print(task.dict())


asyncio.run(main())

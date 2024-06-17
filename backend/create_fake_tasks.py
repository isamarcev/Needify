from src.core.repository import BaseMongoRepository
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.apps.currency.jetton_metadata import NEED_JETTON_METADATA
from src.apps.users.dependencies import MongoDBUserRepository
from src.apps.category.examples import categories
import random
from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.schemas import TaskSchema, JobOfferSchema
from datetime import datetime, timedelta
import asyncio


NUMBER_OF_FAKE_TASKS = 10

async def main():
    config = BaseConfig()
    async_mongo = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
    tasks_repository = BaseMongoRepository(mongo_client=async_mongo, collection_name="tasks")
    categories_repository = BaseMongoRepository(mongo_client=async_mongo, collection_name="categories")
    users_repository = MongoDBUserRepository(config.MONGO_DB_URL, config.MONGO_DB_NAME, collection_name="users")
    users = await users_repository.get_users()

    statuses = [status.value for status in TaskStatusEnum]
    for user_id in users:
        user_id = user_id['telegram_id']
        for status in statuses:
            task = TaskSchema(
                task_id=random.randint(1000000, 1000000000),  # Заменить на логику генерации уникального ID
                title=f"Task {user_id} - {status}",
                description=f"Description for Task {user_id} - {status}",
                category=random.choice(categories)['title'],
                images=["https://incrypted.com/wp-content/uploads/2022/08/ton-100.jpg",
                        "https://pintu-academy.pintukripto.com/wp-content/uploads/2023/12/Ton.png"],
                price=random.randint(50, 555),  # Пример
                currency="USDT",
                status=status,
                poster_id=user_id,
                poster_address=f"User {user_id}'s address",
                deadline=datetime.now() + timedelta(days=7),
                created_at=datetime.now(),
            )


            if status not in [TaskStatusEnum.PRE_CREATED.value, TaskStatusEnum.PRE_DEPLOYING.value, TaskStatusEnum.DEPLOYING.value]:
                job_offer = {
                    "job_offer_address": "Job offer address",
                    "jetton_master_address": "Jetton master address",
                    "jetton_native_address": NEED_JETTON_METADATA["address"],
                    "state": "Some state",
                    "owner": "Some owner",
                    "vacancies": [{"doer": "Some doer", "telegram_id": 1, "is_chosen": False}],
                }

                if status in [TaskStatusEnum.IN_PROGRESS.value, TaskStatusEnum.COMPLETED.value,
                            TaskStatusEnum.CONFIRMED.value, TaskStatusEnum.FINISHED.value]:
                    job_offer['doer'] = "Some doer"

                task.job_offer = JobOfferSchema(**job_offer)


            await tasks_repository.create(task.dict(by_alias=True))
            print(task.dict())

asyncio.run(main())
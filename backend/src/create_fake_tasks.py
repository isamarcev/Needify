from src.core.repository import BaseMongoRepository
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.apps.currency.jetton_metadata import NEED_JETTON_METADATA
from src.apps.currency.schemas import CreateCurrencySchema, CurrencySchema, MintTokenSchema
from random import randint
from faker import Faker
from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.schemas import CreateTaskSchema
from datetime import datetime
import asyncio
import sys
import os

# sys.path.insert(
#     0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", 'src'))
# )

NUMBER_OF_FAKE_TASKS = 10

async def main():
    faker = Faker()
    config = BaseConfig()
    async_mongo = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
    repository = BaseMongoRepository(mongo_client=async_mongo, collection_name="tasks")
    task = {
        'category': 'Test',
        'currency': 'USDT',
        'poster_address': '0QBweRCnIlV3taoANb6sYxhbTA68diwYGoz8u5Py8M8fPvy7',
        'images': [
            "https://incrypted.com/wp-content/uploads/2022/08/ton-100.jpg",
            "https://pintu-academy.pintukripto.com/wp-content/uploads/2023/12/Ton.png"
        ],
        'native_currency': 'TON',
        'status': TaskStatusEnum.PRE_CREATED
    }

    for i in range(NUMBER_OF_FAKE_TASKS):
        task['title'] = f'Test task {i}'
        task['description'] = faker.text()
        task['price'] = faker.random_number(3, fix_len=True)
        task['deadline'] = faker.date_time()
        task['poster_id'] = faker.random_number(10, fix_len=True)
        task['task_id'] = randint()
        task['created_at'] = datetime.now()
        print(task)
        # created_task = await repository.create(task_for_creating.dict())
    



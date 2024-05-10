from aiokafka import AIOKafkaProducer
from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient

from src.apps.users.database import MongoDBUserRepository
from src.apps.users.manager import UserManager
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.core.producer import KafkaProducer


class UserContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")
    config.from_pydantic(BaseConfig())

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.users.router",
        ],
    )

    producer = providers.Singleton(
        KafkaProducer,
        producer_class=AIOKafkaProducer,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    )

    user_database = providers.Factory(
        MongoDBUserRepository,
        mongo_conn=config.MONGO_DB_URL,
        mongo_db=config.MONGO_DB_NAME,
        collection_name="users",
    )

    user_manager = providers.Singleton(
        UserManager, user_repository=user_database, producer=producer
    )

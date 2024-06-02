from aiokafka import AIOKafkaProducer
from dependency_injector import containers, providers

from src.apps.users.database import MongoDBUserRepository
from src.apps.users.manager import UserManager
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig, config
from src.core.producer import KafkaProducer


def get_user_manager():
    async_mongo = ThreadMongoSingleton(config.MONGO_DB_URL, config.MONGO_DB_NAME)
    return UserManager(
        user_repository=MongoDBUserRepository(
            mongo_conn=async_mongo,
            mongo_db=config.MONGO_DB_NAME,
            collection_name="users",
        ),
        producer=KafkaProducer(
            producer_class=AIOKafkaProducer,
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        ),
    )


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

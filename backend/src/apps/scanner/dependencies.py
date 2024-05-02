from aiokafka import AIOKafkaProducer
from dependency_injector import containers, providers

from src.apps.scanner.manager import ScannerManager
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.core.producer import KafkaProducer
from src.core.provider import get_lite_server_client


class ScannerContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.scanner.router",
        ],
    )

    producer = providers.Singleton(
        KafkaProducer,
        producer_class=AIOKafkaProducer,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    )

    async_mongo = providers.Factory(ThreadMongoSingleton, config.MONGO_DB_URL, config.MONGO_DB_NAME)

    lts_client = providers.Singleton(
        get_lite_server_client,
    )

    scanner_manager = providers.Factory(
        ScannerManager, lt_server_provider=lts_client.provided, producer=producer
    )

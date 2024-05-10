from dependency_injector import containers, providers
from TonTools.Providers.TonCenterClient import TonCenterClient

from src.apps.tasks.manager import TaskManager
from src.apps.TONconnect.connector import get_connector
from src.apps.TONconnect.manager import TONConnectManager
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.core.repository import BaseMongoRepository


class TONConnectContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.TONconnect.router",
        ],
    )

    # category_manager = providers.Provider()
    # wallet_manager = providers.Provider()

    # async_mongo = providers.Factory(ThreadMongoSingleton, config.MONGO_DB_URL, config.MONGO_DB_NAME)
    # async_mongo = providers.Factory(ThreadMongoSingleton, config.MONGO_DB_URL, config.MONGO_DB_NAME)

    # task_database = providers.Factory(
    #     BaseMongoRepository, mongo_client=async_mongo, collection_name="tasks"
    # )

    ton_connect_manager = providers.Factory(
        TONConnectManager,
        provider=providers.Factory(
            TonCenterClient,
            base_url=config.TON_CENTER_URL,
            key=config.TON_CENTER_API_KEY,
            testnet=config.IS_TESTNET,
        ),
        # task_repository=task_database,
        # category_manager=category_manager,
        # wallet_manager=wallet_manager,
    )

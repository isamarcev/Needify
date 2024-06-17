from dependency_injector import containers, providers

from src.apps.currency.manager import CurrencyManager
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.core.repository import BaseMongoRepository


class CurrencyContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.currency.router",
        ],
    )

    async_mongo = providers.Factory(ThreadMongoSingleton, config.MONGO_DB_URL, config.MONGO_DB_NAME)

    currency_database = providers.Factory(
        BaseMongoRepository, mongo_client=async_mongo, collection_name="currency"
    )

    ton_center_client = providers.Dependency()
    ton_lib_client = providers.Dependency()
    lite_client = providers.Dependency()

    currency_manager = providers.Factory(
        CurrencyManager,
        ton_lib_client=ton_lib_client,
        ton_center_client=ton_center_client,
        repository=currency_database,
        lite_client=lite_client,
    )

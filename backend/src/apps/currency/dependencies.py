from dependency_injector import containers, providers

from src.apps.currency.manager import CurrencyManager
from src.apps.utils.database import ThreadMongoSingleton
from src.core.config import BaseConfig
from src.core.provider import get_lite_server_client
from src.core.repository import BaseMongoRepository


class CurrencyContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.currency.router",
        ],
    )

    async_mongo = providers.Factory(
        ThreadMongoSingleton, config.MONGO_DB_URL, config.MONGO_DB_NAME
    )

    currency_database = providers.Factory(
        BaseMongoRepository, mongo_client=async_mongo, collection_name="currency"
    )

    lts_client = providers.Factory(
        get_lite_server_client,
    )

    currency_manager = providers.Factory(
        CurrencyManager,
        lts_client=lts_client,
        repository=currency_database,
    )

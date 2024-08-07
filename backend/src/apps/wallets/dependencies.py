from dependency_injector import containers, providers
from TonTools.Providers.TonCenterClient import TonCenterClient

from src.apps.wallets.manager import WalletManager
from src.core.config import BaseConfig
from src.core.repository import BaseMongoRepository


class WalletContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.wallets.router",
        ],
    )
    producer = providers.Dependency()
    async_mongo = providers.Dependency()

    wallet_database = providers.Factory(
        BaseMongoRepository, mongo_client=async_mongo, collection_name="wallets"
    )

    lite_client = providers.Dependency()

    wallet_manager = providers.Factory(
        WalletManager,
        repository=wallet_database,
        main_wallet_mnemonics=config.hd_wallet_mnemonic_list,
        main_wallet_address=config.HD_WALLET_ADDRESS,
        provider=providers.Factory(
            TonCenterClient, config.TON_CENTER_URL, config.TON_CENTER_API_KEY
        ),
        liteserver_client=lite_client,
        producer=producer,
    )

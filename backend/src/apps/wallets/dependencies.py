from dependency_injector import containers, providers
from TonTools.Providers.TonCenterClient import TonCenterClient

from src.apps.utils.database import ThreadMongoSingleton
from src.apps.wallets.jetton_manager import JettonManager
from src.apps.wallets.manager import WalletManager
from src.core.config import BaseConfig
from src.core.provider import get_tonsdk_center_client
from src.core.repository import BaseMongoRepository


async def get_jetton_manager() -> JettonManager:
    manager = JettonManager(ton_center_client=await get_tonsdk_center_client())
    return manager


class WalletContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.wallets.router",
        ],
    )

    async_mongo = providers.Factory(ThreadMongoSingleton, config.MONGO_DB_URL, config.MONGO_DB_NAME)

    wallet_database = providers.Factory(
        BaseMongoRepository, mongo_client=async_mongo, collection_name="wallets"
    )

    wallet_manager = providers.Factory(
        WalletManager,
        repository=wallet_database,
        main_wallet_mnemonics=config.hd_wallet_mnemonic_list,
        main_wallet_address=config.HD_WALLET_ADDRESS,
        provider=providers.Factory(
            TonCenterClient, config.TON_CENTER_URL, config.TON_CENTER_API_KEY
        ),
    )

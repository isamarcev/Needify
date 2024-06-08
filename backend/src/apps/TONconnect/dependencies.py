from dependency_injector import containers, providers
from TonTools.Providers.TonCenterClient import TonCenterClient

from src.apps.TONconnect.manager import TONConnectManager
from src.core.config import BaseConfig


class TONConnectContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.TONconnect.router",
        ],
    )

    ton_connect_manager = providers.Factory(
        TONConnectManager,
        provider=providers.Factory(
            TonCenterClient,
            base_url=config.TON_CENTER_URL,
            key=config.TON_CENTER_API_KEY,
            testnet=config.IS_TESTNET,
        ),
    )

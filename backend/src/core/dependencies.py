from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from dependency_injector import containers, providers

from src.apps.category.dependencies import CategoryContainer
from src.apps.currency.dependencies import CurrencyContainer
from src.apps.tasks.dependencies import TaskContainer
from src.apps.TONconnect.dependencies import TONConnectContainer
from src.apps.users.dependencies import UserContainer
from src.apps.users.events import UserEventsEnum
from src.apps.wallets.dependencies import WalletContainer
from src.apps.wallets.events import WalletTopicsEnum
from src.core.config import BaseConfig
from src.core.message_hub import MessageHub
from src.core.producer import KafkaProducer
from src.core.provider import get_lite_server_client


class CoreContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")
    config.from_pydantic(BaseConfig())

    task_container = providers.Container(
        TaskContainer,
        config=config,
    )

    ton_connect_manager = providers.Container(
        TONConnectContainer,
        config=config,
    )

    user_container = providers.Container(
        UserContainer,
        config=config,
    )

    currency_container = providers.Container(
        CurrencyContainer,
        config=config,
    )

    category_container = providers.Container(
        CategoryContainer,
        config=config,
    )

    wallet_container = providers.Container(
        WalletContainer,
        config=config,
    )

    kafka_consumer = providers.Singleton(
        AIOKafkaConsumer,
        *UserEventsEnum.topics_list(),
        *WalletTopicsEnum.topics_list(),
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        group_id="the_open_times_group",
    )

    producer = providers.Singleton(
        KafkaProducer,
        producer_class=AIOKafkaProducer,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    )

    lts_client = providers.Factory(
        get_lite_server_client,
    )

    # scanner_manager = providers.Factory(
    #     ScannerManager, lt_server_provider=lts_client, producer=producer
    # )

    handlers = {
        UserEventsEnum.USER_CREATED: [
            user_container.container.user_manager.provided.handle_created_user,
        ],
        WalletTopicsEnum.FOUNDED_DEPOSIT_WALLET: [
            wallet_container.container.wallet_manager.provided.handle_wallet_created,
        ],
    }

    message_hub = providers.Factory(
        MessageHub,
        consumer=kafka_consumer,
        handlers=handlers,
    )

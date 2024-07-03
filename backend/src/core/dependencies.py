from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from dependency_injector import containers, providers
from redis.asyncio import Redis
from telebot.async_telebot import AsyncTeleBot
from TonTools.Providers.TonCenterClient import TonCenterClient

from src.apps.category.dependencies import CategoryContainer
from src.apps.currency.dependencies import CurrencyContainer
from src.apps.job_offer.dependencies import JobOfferContainer
from src.apps.notificator.dependencies import NotificatorContainer
from src.apps.scanner.service import BlockScanner
from src.apps.tasks.dependencies import TaskContainer
from src.apps.TONconnect.dependencies import TONConnectContainer
from src.apps.users.dependencies import UserContainer
from src.apps.users.events import UserEventsEnum
from src.apps.utils.database import ThreadMongoSingleton
from src.apps.wallets.dependencies import WalletContainer
from src.apps.wallets.events import WalletTopicsEnum
from src.core.config import BaseConfig
from src.core.local_storage import RedisStorage
from src.core.message_hub import MessageHub
from src.core.producer import KafkaProducer
from src.core.provider import get_lite_client, get_ton_lib_client


class CoreContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")
    config.from_pydantic(BaseConfig())

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.scanner.router",
            "src.apps.job_offer.router",
            "src.apps.tasks.router",
        ]
    )

    producer = providers.Singleton(
        KafkaProducer,
        producer_class=AIOKafkaProducer,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    )
    async_mongo = providers.Singleton(
        ThreadMongoSingleton, config.MONGO_DB_URL, config.MONGO_DB_NAME
    )
    ton_center_client = providers.Singleton(
        TonCenterClient, base_url=config.TON_CENTER_URL, key=config.TON_CENTER_API_KEY
    )

    ton_lib_client = providers.Singleton(
        get_ton_lib_client,
    )

    ton_connect_manager = providers.Container(
        TONConnectContainer,
        config=config,
    )

    user_container = providers.Container(
        UserContainer,
        config=config,
        producer=producer,
    )
    lite_client = providers.Singleton(
        get_lite_client,
        liteserver_index=3,
    )
    currency_container = providers.Container(
        CurrencyContainer,
        ton_center_client=ton_center_client,
        ton_lib_client=ton_lib_client,
        config=config,
        lite_client=lite_client,
    )

    wallet_container = providers.Container(
        WalletContainer,
        config=config,
        lite_client=lite_client,
        producer=producer,
        async_mongo=async_mongo,
    )
    category_container = providers.Container(
        CategoryContainer,
        config=config,
    )

    bot = providers.Singleton(
        AsyncTeleBot,
        token=config.BOT_TOKEN,
    )

    notificator_container = providers.Container(
        NotificatorContainer,
        config=config,
        bot=bot,
    )

    task_container = providers.Container(
        TaskContainer,
        config=config,
        currency_manager=currency_container.currency_manager,
        wallet_manager=wallet_container.wallet_manager,
        user_manager=user_container.user_manager,
        category_manager=category_container.category_manager,
        async_mongo=async_mongo,
        notificator_manager=notificator_container.notificator_manager,
    )

    job_offer_container = providers.Container(
        JobOfferContainer,
        category_manager=category_container.category_manager,
        wallet_manager=wallet_container.wallet_manager,
        currency_manager=currency_container.currency_manager,
        user_manager=user_container.user_manager,
        task_manager=task_container.task_manager,
        config=config,
        lite_client=lite_client,
        ton_lib_client=ton_lib_client,
    )

    kafka_consumer = providers.Singleton(
        AIOKafkaConsumer,
        *UserEventsEnum.topics_list(),
        *WalletTopicsEnum.topics_list(),
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        group_id="the_open_times_group",
    )

    lts_client = providers.Factory(
        get_ton_lib_client,
    )

    local_storage = providers.Resource(RedisStorage, Redis, connect_url=config.REDIS_URL)

    scanner_service = providers.Factory(
        BlockScanner,
        local_storage=local_storage,
        lite_client=lite_client,
        task_manager=task_container.task_manager.provided,
        job_offer_manager=job_offer_container.job_offer_manager.provided,
        producer=producer,
        # wallet_manager=wallet_app.wallet_manager,
        # currency_manager=currency_app.currency_manager,
        # settings_service=settings_service,
    )

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



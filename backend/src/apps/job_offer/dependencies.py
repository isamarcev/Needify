from dependency_injector import containers, providers

from src.apps.job_offer.factory import JobOfferFactory
from src.apps.job_offer.manager import JobOfferManager
from src.apps.TONconnect.manager import TONConnectManager
from src.apps.transaction.service import TransactionService
from src.core.config import BaseConfig


class JobOfferContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.job_offer.router",
        ],
    )
    category_manager = providers.Dependency()
    wallet_manager = providers.Dependency()
    currency_manager = providers.Dependency()
    user_manager = providers.Dependency()
    task_manager = providers.Dependency()

    lite_client = providers.Dependency()
    ton_lib_client = providers.Dependency()

    job_offer_factory = providers.Factory(JobOfferFactory)

    ton_connect_manager = providers.Singleton(
        TONConnectManager,
    )

    transaction_service = providers.Singleton(
        TransactionService,
    )

    job_offer_manager = providers.Factory(
        JobOfferManager,
        category_manager=category_manager,
        wallet_manager=wallet_manager,
        currency_manager=currency_manager,
        user_manager=user_manager,
        task_manager=task_manager,
        job_offer_factory=job_offer_factory,
        ton_connect_manager=ton_connect_manager,
        lite_client=lite_client,
        ton_lib_client=ton_lib_client,
        transaction_service=transaction_service,
    )

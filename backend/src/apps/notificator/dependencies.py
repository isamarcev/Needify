from dependency_injector import containers, providers

from src.core.config import BaseConfig


class NotificatorContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.notificator.router",
            "src.apps.job_offer.router",
        ],
    )

    bot = providers.Dependency()

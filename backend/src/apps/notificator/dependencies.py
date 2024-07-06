from dependency_injector import containers, providers
from telebot.async_telebot import AsyncTeleBot

from src.apps.notificator.manager import NotificatorManager
from src.core.config import BaseConfig


class NotificatorContainer(containers.DeclarativeContainer):
    config: BaseConfig = providers.Configuration("config")

    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.apps.notificator.router",
            "src.apps.job_offer.router",
        ],
    )

    bot: AsyncTeleBot = providers.Dependency()

    notificator_manager = providers.Factory(
        NotificatorManager,
        bot=bot,
        config=config,
    )

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from telebot.async_telebot import AsyncTeleBot, types

from src.apps.notificator.dependencies import NotificatorContainer
from src.apps.notificator.schemas import SendNotificationSchema
from src.apps.notificator.manager import NotificatorManager
from src.core.config import BaseConfig

notificator_router = APIRouter()


@notificator_router.post("/send")
@inject
async def get_deploy_job_offer_message(
    data: SendNotificationSchema,
    # config: BaseConfig = Depends(Provide[NotificatorContainer.config]),
    # bot: AsyncTeleBot = Depends(Provide[NotificatorContainer.bot]),
    notificator_manager: NotificatorManager = Depends(Provide[NotificatorContainer.notificator_manager]), 
):
    # kb = types.InlineKeyboardMarkup(row_width=1)
    # kb.add(types.InlineKeyboardButton("Open App", web_app=types.WebAppInfo(config["WEB_APP_URL"])))
    # await bot.send_message(data.user_telegram_id, data.text, reply_markup=kb)
    await notificator_manager.send_notification(data.user_telegram_id, data.task_id, data.task_title, data.new_task_status)
    return {"status": "ok"}

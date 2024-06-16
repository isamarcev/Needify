import logging
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from src.apps.notificator.schemas import SendNotificationSchema
from telebot.async_telebot import AsyncTeleBot, types
from src.apps.notificator.dependencies import NotificatorContainer
from src.core.config import BaseConfig


notificator_router = APIRouter()

@notificator_router.post("/send")
@inject
async def get_deploy_job_offer_message(
    data: SendNotificationSchema,
    config: BaseConfig = Depends(Provide[NotificatorContainer.config]),
    bot: AsyncTeleBot = Depends(Provide[NotificatorContainer.bot]),
):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton('Open App', web_app=types.WebAppInfo(config['WEB_APP_URL'])))
    await bot.send_message(data.user_telegram_id, data.text, reply_markup=kb)
    return {"status": "ok"} 

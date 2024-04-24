from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

from src.core.config import env_config

# from aiogram.utils.i18n import gettext as _

main_router = Router()


@main_router.message(Command(commands=["start"]))
async def command_start(message: Message, state: FSMContext) -> None:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Open", web_app=WebAppInfo(url=env_config.telegram.WEB_APP_URL))]],
    )
    await message.answer(
        "Hello World!",
        reply_markup=keyboard,
    )
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from src.core.config import env_config


def get_welcome_message():
    text = "Welcome to our service! 🚀. We are glad to see you here! 😊"
    return text


def get_welcome_keyboard():
    keyboard = [
        [KeyboardButton(text="Open", web_app=WebAppInfo(url=env_config.telegram.WEB_APP_URL))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

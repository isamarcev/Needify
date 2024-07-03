from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from src.core.config import env_config


def get_welcome_message():
    text = (
        "🎉 **Welcome to Our Service!** 🚀\n\n"
        "We are absolutely thrilled to have you here! 😊\n\n"
        "To get started, simply click the button below and dive into an amazing experience. 🌟\n\n"
        "While we continue to enhance our service, don't miss out on the chance to invite your "
        "friends and earn exciting rewards! 💰\n\n"
        "Thank you for joining us, and let's make this journey unforgettable together! 🙌"
    )
    return text


def get_welcome_keyboard():
    keyboard = [
        [KeyboardButton(text="Open", web_app=WebAppInfo(url=env_config.telegram.WEB_APP_URL))]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

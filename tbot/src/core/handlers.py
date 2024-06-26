from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, WebAppInfo

from src.core.config import env_config
from src.core.messages import get_welcome_keyboard, get_welcome_message
from src.referral.utils import get_referral_link
from src.users.manager import get_user_manager

main_router = Router()


@main_router.message(Command(commands=["start"]))
async def command_start(message: Message, state: FSMContext) -> None:
    user_manager = get_user_manager()
    exist_user = await user_manager.get_user(message.from_user.id)
    if not exist_user:
        if message.chat.type == "private":
            start_command = message.text
            referrer_id = str(start_command[7:])
            if referrer_id != "":
                await user_manager.referral_job_done(user_id=int(referrer_id))
                await user_manager.add_user(user=message.from_user)
                referral_link = get_referral_link(
                    user=message.from_user, channel_name=env_config.telegram.BOT_NICKNAME
                )
                user = await user_manager.get_user(message.from_user.id)
                await message.answer(
                    f"Welcome {message.from_user.first_name}!,"
                    " Your friend already got reward. You can too. \n"
                    f"Your referral link: {referral_link}. \n"
                    f"You current balance is {user.balance} NEED. \n",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton(text="Invite friends", url=referral_link)]],
                        resize_keyboard=True,
                    ),
                )
                return
            else:
                await user_manager.add_user(user=message.from_user)
                await message.answer(
                    get_welcome_message(),
                    keyboard=get_welcome_keyboard(),
                )
                return
    else:
        referral_link = get_referral_link(
            user=message.from_user, channel_name=env_config.telegram.BOT_NICKNAME
        )
        user = await user_manager.get_user(message.from_user.id)
        await message.answer(
            "You are already in our system. You can invite friends and get rewards. \n"
            f"You balance: {user.balance} NEED. \n"
            f"Your referral link to invite friends: {referral_link}. \n"
            f"You can browse our app and progress in by the button below. ",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="Open App", web_app=WebAppInfo(url=env_config.telegram.WEB_APP_URL)
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )

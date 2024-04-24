from aiogram import Bot
from aiogram.methods import SetMyCommands
from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Go Go Go 🚀"),
    ]
    await bot(SetMyCommands(commands=commands))

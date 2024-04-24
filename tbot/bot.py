import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from src.core.handlers import main_router
from src.utils.commands import set_commands

from src.core.config import env_config
from src.core.database import redis_storage

# Bot token can be obtained via https://t.me/BotFather
TOKEN = env_config.telegram.BOT_TOKEN

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher(storage=redis_storage)
dp.include_router(main_router)

bot = Bot(TOKEN)

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
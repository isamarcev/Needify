import urllib.parse

from telebot.async_telebot import AsyncTeleBot, types


class NotificatorManager:
    def __init__(self, bot: AsyncTeleBot, config: dict):
        self.bot = bot
        self.config = config

    async def send_notification(
        self, user_telegram_id: int, task_id: int, task_title: str, new_task_status: str
    ):
        text = f"📋 Your task: <b>{task_title}</b>\n has new status <b>{new_task_status}</b>"
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton(
                "Open Task",
                web_app=types.WebAppInfo(
                    urllib.parse.urljoin(self.config["WEB_APP_URL"], f"task-detail/{task_id}")
                ),
            )
        )

        await self.bot.send_message(user_telegram_id, text, reply_markup=kb, parse_mode="HTML")

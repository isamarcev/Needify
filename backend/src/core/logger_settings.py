import asyncio
import logging.config

import yaml
from colorlog import ColoredFormatter
from gunicorn import glogging
from pythonjsonlogger import jsonlogger
from telebot.async_telebot import AsyncTeleBot

from src.core.config import BASE_DIR, CONTEXT_ID, LOG_DIR, config


class TelegramHandler(logging.Handler):
    def _resolve_message(self, record: logging.LogRecord) -> str:
        if issubclass(record.msg.__class__, Exception):
            message = record.msg.__class__.__name__ + ": " + str(record.msg)
        else:
            # Try to get error from record.exc_info
            if record.exc_info and record.exc_info[1] is not None:
                exc = record.exc_info[1]
                message = exc.__class__.__name__ + ": " + str(exc)
            else:
                message = record.msg

        return message

    def emit(self, record):
        bot = AsyncTeleBot(token=config.BOT_TOKEN)
        text = self._resolve_message(record)
        try:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(
                bot.send_message(chat_id=config.ADMIN_TELEGRAM_ID, text=text), loop=loop
            )
        except Exception as e:
            print(f"Failed to send log: {e}")


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        log_record["context_id"] = CONTEXT_ID.get()


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # We set request id, so we can use it in the formatter to show it in the log records.
        # Also, this fields will be added to the graylog extra fields and will be searchable.
        context_id = CONTEXT_ID.get()

        if context_id:
            record.context_id = context_id
            record.short_context_id = context_id[:3] + "..." + context_id[-3:]
        else:
            record.context_id = ""
            record.short_context_id = ""

        # setattr(record, "api_source", settings.GRAYLOG_API_SOURCE)

        return super().format(record)


class CustomColoredFormatter(ColoredFormatter, CustomFormatter):
    pass


# class CustomGraylogHandler(graypy.GELFUDPHandler):
#     def __init__(self, host: str, port: str):
#         super().__init__(host, int(port))


def setup_logging():
    settings_module = "DEV"
    if settings_module == "DEV":
        file_name = BASE_DIR / "logging.yml"
    elif settings_module == "PROD":
        file_name = BASE_DIR / "logging.prod.yml"
    else:
        raise ValueError(f"Unknown settings module: {settings_module}")

    with open(file_name) as log_file:
        content = log_file.read()

    # graylog_host, graylog_port = settings.GRAYLOG_BIND.split(":") if settings.GRAYLOG_BIND
    # else None
    graylog_host, graylog_port = "localhost", "12201"
    log_config = content.format(
        logdir=LOG_DIR, graylog_host=graylog_host, graylog_port=graylog_port
    )

    logging.config.dictConfig(yaml.safe_load(log_config))


class GunicornLogger(glogging.Logger):
    def setup(self, cfg):
        setup_logging()

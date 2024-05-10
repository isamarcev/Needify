from pytonconnect import TonConnect

from src.apps.TONconnect.ts_storage import TcStorage
from src.core.config import config

# import config
# from tc_storage import TcStorage


def get_connector(chat_id: int):
    return TonConnect(config.MANIFEST_URL, storage=TcStorage(chat_id))

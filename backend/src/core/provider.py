from pathlib import Path

import requests
from pytonlib import TonlibClient
from TonTools import TonCenterClient

from src.core.config import config


async def get_lite_server_client() -> TonlibClient:
    url = "https://ton.org/testnet-global.config.json"

    ls_config = requests.get(url).json()

    keystore_dir = "/tmp/ton_keystore"
    Path(keystore_dir).mkdir(parents=True, exist_ok=True)

    client = TonlibClient(
        ls_index=config.LITESERVER_INDEX,
        config=ls_config,
        keystore=keystore_dir,
        tonlib_timeout=25,
    )

    await client.init()
    return client


async def get_tonsdk_center_client():
    provider = TonCenterClient(base_url=config.TON_CENTER_URL, key=config.TON_CENTER_API_KEY)
    return provider

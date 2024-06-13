from pathlib import Path

import requests
import TonTools
from pytoniq import LiteClient
from pytonlib import TonlibClient
from TonTools import TonCenterClient
from TonTools.Providers.LsClient import LsClient

from src.core.config import config


async def get_ton_lib_client() -> TonlibClient:
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


def get_lite_server_config() -> dict:
    url = "https://ton.org/testnet-global.config.json"
    return requests.get(url).json()


def get_lite_client(liteserver_index: int = 0) -> LiteClient:
    ls_config = get_lite_server_config()
    client = LiteClient.from_config(
        config=ls_config, ls_i=liteserver_index, trust_level=2, timeout=15
    )

    return client


def get_ton_client(liteserver_index: int = 0) -> TonlibClient:
    ls_config = get_lite_server_config()
    keystore_dir = "/tmp/ton_keystore"
    Path(keystore_dir).mkdir(parents=True, exist_ok=True)

    client = TonlibClient(
        ls_index=liteserver_index,
        config=ls_config,
        keystore=keystore_dir,
        tonlib_timeout=25,
    )
    return client


async def get_toncenter_client() -> TonCenterClient:
    provider = TonCenterClient(
        base_url=config.TON_CENTER_URL, key=config.TON_CENTER_API_KEY, testnet=config.IS_TESTNET
    )
    return provider


async def get_liteserver_client(ls_index: int = 0) -> LsClient:
    url = "https://ton.org/testnet-global.config.json"
    ls_config = requests.get(url).json()
    keystore_dir = "/tmp/ton_keystore"
    Path(keystore_dir).mkdir(parents=True, exist_ok=True)
    LsClient.config = ls_config
    client = LsClient(ls_index=ls_index, default_timeout=30, addresses_form="user_friendly")
    await client.init_tonlib()
    return client


async def get_tonsdk_center_client():
    provider = TonCenterClient(base_url=config.TON_CENTER_URL, key=config.TON_CENTER_API_KEY)
    add = "kQBd2viWmPE1iA0GBP0szwbYVCXmzZFENnSvmKFXWW-af2Rc"
    state = await provider.get_jetton_data(add)
    print(state)
    return provider


async def tontools_get_data():
    client = TonTools.TonCenterClient(key=config.TON_CENTER_API_KEY)

    jetton_minter = TonTools.Jetton(
        data="EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs", provider=client
    )
    await jetton_minter.update()
    print(jetton_minter)


# async def main():
#     client = await get_ton_lib_client()
#     add = "kQBd2viWmPE1iA0GBP0szwbYVCXmzZFENnSvmKFXWW-af2Rc"
#     stack = (await client.raw_run_method(address=add, method="get_jetton_data", stack_data=[]))[
#         "stack"
#     ]
#     print(stack)
#     await client.close()
#
#
# if __name__ == "__main__":
#     import asyncio
#
#     asyncio.get_event_loop().run_until_complete(main())

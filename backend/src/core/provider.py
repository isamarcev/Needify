from contextlib import asynccontextmanager
from pathlib import Path

import TonTools
import requests
from TonTools.Contracts.Jetton import Jetton
from TonTools.Providers.LsClient import LsClient
from pytoniq import LiteClient
from pytonlib import TonlibClient
from TonTools import TonCenterClient

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


async def get_lite_client() -> LiteClient:
    client = LiteClient.from_testnet_config(
        ls_i=2, trust_level=2, timeout=15
    )
    await client.connect()
    return client


async def get_toncenter_client() -> TonCenterClient:
    provider = TonCenterClient(
        base_url=config.TON_CENTER_URL, key=config.TON_CENTER_API_KEY, testnet=config.IS_TESTNET
    )
    return provider


async def get_liteserver_client() -> LsClient:
    url = "https://ton.org/testnet-global.config.json"
    ls_config = requests.get(url).json()
    keystore_dir = "/tmp/ton_keystore"
    Path(keystore_dir).mkdir(parents=True, exist_ok=True)
    LsClient.config = ls_config
    client = LsClient(ls_index=2, default_timeout=30, addresses_form='user_friendly')
    await client.init_tonlib()
    jetton = Jetton('EQBl3gg6AAdjgjO2ZoNU5Q5EzUIl8XMNZrix8Z5dJmkHUfxI', provider=client)
    print(jetton)  # Jetton({"jetton_master_address": "EQBl3gg6AAdjgjO2ZoNU5Q5EzUIl8XMNZrix8Z5dJmkHUfxI"})

    await jetton.update()
    print(
        jetton)  # Jetton({"supply": 4600000000000000000, "jetton_master_address": "EQBl3gg6AAdjgjO2ZoNU5Q5EzUIl8XMNZrix8Z5dJmkHUfxI", "decimals": 9, "symbol": "LAVE", "name": "Lavandos", "description": "This is a universal token for use in all areas of the decentralized Internet in the TON blockchain, web3, Telegram bots, TON sites. Issue of 4.6 billion coins. Telegram channels: Englishversion: @lave_eng \u0420\u0443\u0441\u0441\u043a\u043e\u044f\u0437\u044b\u0447\u043d\u0430\u044f \u0432\u0435\u0440\u0441\u0438\u044f: @lavet", "image": "https://i.ibb.co/Bj5KqK4/IMG-20221213-115545-207.png", "token_supply": 4600000000.0})

    return client


async def get_tonsdk_center_client():
    provider = TonCenterClient(
        base_url=config.TON_CENTER_URL, key=config.TON_CENTER_API_KEY
    )
    add = "kQBd2viWmPE1iA0GBP0szwbYVCXmzZFENnSvmKFXWW-af2Rc"
    state = await provider.get_jetton_data(add)
    print(state)
    return provider

async def tontools_get_data():
    client = TonTools.TonCenterClient(
        key=config.TON_CENTER_API_KEY
    )

    jetton_minter = TonTools.Jetton(data="EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs", provider=client)
    await jetton_minter.update()
    print(jetton_minter)

async def main():
    client = await get_ton_lib_client()
    add = "kQBd2viWmPE1iA0GBP0szwbYVCXmzZFENnSvmKFXWW-af2Rc"
    stack = (await client.raw_run_method(address=add, method="get_jetton_data", stack_data=[]))["stack"]
    print(stack)
    await client.close()


if __name__ == '__main__':
    import asyncio

    asyncio.get_event_loop().run_until_complete(main())


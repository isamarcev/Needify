from mint_bodies import create_state_init_jetton, increase_supply
from pytonlib import TonlibClient
from tonsdk.utils import to_nano

from src.apps.utils.wallet import get_wallet_info_by_mnemonic
from src.core.config import config
from src.core.provider import get_ton_lib_client


async def get_seqno(client: TonlibClient, address: str):
    data = await client.raw_run_method(method="seqno", stack_data=[], address=address)
    return int(data["stack"][0][1], 16)


async def deploy_minter():
    state_init, jetton_address = create_state_init_jetton()
    client = await get_ton_lib_client()
    hd_wallet_info = get_wallet_info_by_mnemonic(
        config.hd_wallet_mnemonic_list,
        config.WORKCHAIN,
        is_testnet=config.IS_TESTNET,
    )
    seqno = await get_seqno(client, hd_wallet_info.get("wallet_address"))
    wallet = hd_wallet_info.get("wallet")
    query = wallet.create_transfer_message(
        to_addr=jetton_address,
        amount=to_nano(config.AMOUNT_TON_TO_DEPLOY, "ton"),
        seqno=seqno,
        state_init=state_init,
    )
    await client.raw_send_message(query["message"].to_boc(False))


async def mint_tokens():

    body = increase_supply(1000000000)
    client = await get_ton_lib_client()
    seqno = await get_seqno(client, config.HD_WALLET_ADDRESS)
    hd_wallet_info = get_wallet_info_by_mnemonic(
        config.hd_wallet_mnemonic_list,
        config.WORKCHAIN,
        is_testnet=config.IS_TESTNET,
    )
    wallet = hd_wallet_info.get("wallet")
    query = wallet.create_transfer_message(
        to_addr=config.HD_WALLET_ADDRESS,
        amount=to_nano(config.AMOUNT_TON_TO_DEPLOY, "ton"),
        seqno=seqno,
        payload=body,
    )

    await client.raw_send_message(query["message"].to_boc(False))


#
# if __name__ == '__main__':
#     import asyncio
#
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(deploy_minter())
#     # loop.run_until_complete(mint_tokens())

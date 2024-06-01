import asyncio
import datetime
import time

import pytonconnect
import tonsdk
from pytonconnect import TonConnect
from pytonconnect.exceptions import UserRejectsError
from pytoniq_core import Address
from tonsdk.utils import bytes_to_b64str
from TonTools.Contracts.Jetton import Jetton
from TonTools.Contracts.Wallet import Wallet

from src.apps.TONconnect.schemas import ConnectDepositSchema
from src.apps.TONconnect.ts_storage import TcStorage
from src.core.config import config


class TONConnectManager:
    def __init__(self, provider):
        self.provider = provider

    def get_connector(self, chat_id: int):
        return TonConnect(config.MANIFEST_URL, storage=TcStorage(chat_id))

    async def connect_wallet(self, connector, wallet_name: str):
        wallets_list = connector.get_wallets()
        wallet = None

        print(f"Wallets list: {wallets_list}")
        # raise ValueError('Connection failed')
        for w in wallets_list:
            if w["name"] == wallet_name:
                wallet = w

        if wallet is None:
            raise Exception(f"Unknown wallet: {wallet_name}")

        generated_url = await connector.connect(wallet)
        print(f"Generated URL: {generated_url}")

        for i in range(1, 180):
            await asyncio.sleep(1)
            if connector.connected:
                if connector.account.address:
                    wallet_address = connector.account.address
                    wallet_address = Address(wallet_address).to_str(is_bounceable=False)
                    # await message.answer(
                    #     f'You are connected with jetton_master_address <code>{wallet_address}</code>',
                    #     reply_markup=mk_b.as_markup())
                    print(f"Connected with address: {wallet_address}")
                    return wallet_address
        raise ValueError("Connection failed")
        # return

    async def test(self, data: ConnectDepositSchema):
        connector = self.get_connector(data.action_by_user_id)
        wallet_address = await self.connect_wallet(connector, data.wallet_name)
        connected = await connector.restore_connection()
        if not connected:
            raise ValueError("Connection failed")
        test_job = test_job_offer
        dep = test_job.get_deploy_message()
        transaction = {
            "valid_until": int(time.time() + 3600),
            "messages": [
                dep
                # get_jetton_transfer_message(
                #     jetton_wallet_address=jetton_master_address,
                #     recipient_address=recipient_address,
                #     transfer_fee=int(data.transfer_fee * 10**9),
                #     jettons_amount=int(data.jettons_amount * 10**9),
                #     response_address=response_,
                # ),
                # get_jetton_transfer_message(
                #     jetton_wallet_address=second_jetton_master,
                #     recipient_address=recipient_address,
                #     transfer_fee=int(data.transfer_fee * 10 ** 9),
                #     jettons_amount=int(data.jettons_amount * 10 ** 9 * 2),
                #     response_address=response_
                # )
            ],
        }
        print(transaction, "TRANSACTION")
        try:
            await asyncio.wait_for(
                connector.send_transaction(transaction=transaction), 300
            )
        except asyncio.TimeoutError:
            raise ValueError("Timeout error!")
        except UserRejectsError as e:
            raise ValueError("You rejected the transaction!")
        except Exception as e:
            raise ValueError(f"Unknown error: {e}")
        except KeyboardInterrupt:
            await connector.disconnect()

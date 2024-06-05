import asyncio
import logging
import time

from pytonconnect import TonConnect
from pytonconnect.exceptions import UserRejectsError
from pytoniq_core import Address

from src.apps.job_offer.schemas import TONConnectMessageResponse
from src.apps.tasks.schemas import TaskSchema
from src.apps.TONconnect.schemas import ConnectDepositSchema
from src.apps.TONconnect.ts_storage import TcStorage
from src.core.config import config

logger = logging.getLogger("root")


class TONConnectManager:
    def get_connector(self, chat_id: int):
        return TonConnect(config.MANIFEST_URL, storage=TcStorage(chat_id))

    async def connect_wallet(self, connector, wallet_name: str):
        wallets_list = connector.get_wallets()
        wallet = None

        logger.info(f"Wallets list: {wallets_list}")
        # raise ValueError('Connection failed')
        for w in wallets_list:
            if w["name"] == wallet_name:
                wallet = w

        if wallet is None:
            raise Exception(f"Unknown wallet: {wallet_name}")

        generated_url = await connector.connect(wallet)
        logger.info(f"Generated URL: {generated_url}")

        for i in range(1, 180):  # noqa
            await asyncio.sleep(1)
            if connector.connected and connector.account.address:
                wallet_address = connector.account.address
                wallet_address = Address(wallet_address).to_str(is_bounceable=False)
                # await message.answer(
                #     f'You are connected with address <code>{wallet_address}</code>',
                #     reply_markup=mk_b.as_markup())
                logger.info(f"Connected with address: {wallet_address}")
                return wallet_address
        raise ValueError("Connection failed")
        # return

    async def test_connect_by_task(
        self, task: TaskSchema, messages: TONConnectMessageResponse
    ):
        wallet_name = "Tonkeeper"
        # wallet_name = "Wallet"
        connector = self.get_connector(task.poster_id)
        await self.connect_wallet(connector, wallet_name)
        connected = await connector.restore_connection()
        if not connected:
            raise ValueError("Connection failed")

        transaction = messages.dict()
        await self.send_transaction(transaction, connector)
        return

    async def test(self, data: ConnectDepositSchema):
        connector = self.get_connector(data.action_by_user_id)
        await self.connect_wallet(connector, data.wallet_name)
        connected = await connector.restore_connection()
        if not connected:
            raise ValueError("Connection failed")
        test_job = "test_job"
        dep = test_job.get_deploy_message()
        transaction = {
            "valid_until": int(time.time() + 3600),
            "messages": [
                dep
                # get_jetton_transfer_message(
                #     jetton_wallet_address=address,
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
            await asyncio.wait_for(connector.send_transaction(transaction=transaction), 300)
        except asyncio.TimeoutError:
            raise ValueError("Timeout error!") from None
        except UserRejectsError:
            raise ValueError("You rejected the transaction!") from None
        except Exception as e:
            raise ValueError(f"Unknown error: {e}") from e
        except KeyboardInterrupt:
            await connector.disconnect()

    async def send_transaction(self, transaction: dict, connector):
        try:
            await asyncio.wait_for(connector.send_transaction(transaction=transaction), 300)
        except asyncio.TimeoutError:
            raise ValueError("Timeout error!") from None
        except UserRejectsError:
            raise ValueError("You rejected the transaction!") from None
        except Exception as e:
            raise ValueError(f"Unknown error: {e}") from e
        except KeyboardInterrupt:
            await connector.disconnect()

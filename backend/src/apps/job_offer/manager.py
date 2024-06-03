import base64
import logging
import time

from pytoniq import LiteClient
from pytonlib import TonlibClient
from ton.utils import read_address
from tonsdk.boc import Cell
from tonsdk.utils import b64str_to_bytes, to_nano
from TonTools.Contracts.Jetton import JettonWallet

from src.apps.category.manager import CategoryManager
from src.apps.currency.manager import CurrencyManager
from src.apps.currency.schemas import CurrencySchema
from src.apps.job_offer.factory import JobOfferFactory
from src.apps.job_offer.schemas import JobOfferMessageDeployResponseSchema, JobOfferMessageSchema
from src.apps.tasks.manager import TaskManager
from src.apps.TONconnect.manager import TONConnectManager
from src.apps.users.manager import UserManager
from src.apps.users.schemas import UserSchema
from src.apps.utils.exceptions import JsonHTTPException
from src.apps.wallets.manager import WalletManager
from src.apps.wallets.utils import get_jetton_transfer_message
from src.core.config import config


class JobOfferManager:
    def __init__(
        self,
        task_manager: TaskManager,
        category_manager: CategoryManager,
        wallet_manager: WalletManager,
        currency_manager: CurrencyManager,
        user_manager: UserManager,
        job_offer_factory: JobOfferFactory,
        ton_connect_manager: TONConnectManager,
        lite_client: LiteClient,
        ton_lib_client: TonlibClient,
    ):
        self.task_manager = task_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.currency_manager = currency_manager
        self.user_manager = user_manager
        self.job_offer_factory = job_offer_factory
        self.ton_connect_manager = ton_connect_manager
        self.lite_client = lite_client
        self.ton_lib_client = ton_lib_client

    async def get_job_offer_chain_state(self, data: JobOfferMessageSchema):
        task = await self.task_manager.get_by_task_id(data.task_id)
        native_currency: CurrencySchema = await self.currency_manager.get_native_currency()
        task_currency: CurrencySchema = await self.currency_manager.get(task.currency)
        job_offer = await self.job_offer_factory.create_job_offer(
            task, native_currency, task_currency
        )
        result = await self.ton_lib_client.raw_run_method(
            job_offer.address.to_string(), "job_data", []
        )
        logging.info(f"get_wallet_data result: {result}")
        return await self.parse_job_offer(result)

    async def create_deploy_message(self, data: JobOfferMessageSchema):
        task = await self.task_manager.get_by_task_id(data.task_id)
        user: UserSchema = await self.user_manager.get_user_by_telegram_id(data.action_by_user)
        if task.poster_id != user.telegram_id:
            raise JsonHTTPException(
                status_code=400,
                error_description="You are not the owner of this task",
                error_name="BadRequest",
            )
        if not task:
            raise JsonHTTPException(
                status_code=404,
                error_description=f"Task with id {data.task_id} not found",
                error_name="NotFound",
            )
        native_currency: CurrencySchema = await self.currency_manager.get_native_currency()
        task_currency: CurrencySchema = await self.currency_manager.get(task.currency)
        user_task_wallet: JettonWallet = await self.currency_manager.get_jetton_wallet(
            task_currency.address, task.poster_address
        )
        user_native_wallet: JettonWallet = await self.currency_manager.get_jetton_wallet(
            native_currency.address, task.poster_address
        )
        await self.task_manager.check_poster_balance_for_deploy(
            task.poster_address, task.price, task_currency, native_currency
        )
        job_offer = await self.job_offer_factory.create_job_offer(
            task, native_currency, task_currency
        )
        job_offer_deploy_message = job_offer.get_deploy_message()
        task_currency_transfer_message = get_jetton_transfer_message(
            jetton_wallet_address=user_task_wallet.address,
            recipient_address=job_offer.address.to_string(),
            transfer_fee=to_nano(config.FORWARD_TON_TRANSFER_AMOUNT, "ton"),
            jettons_amount=job_offer.price,
            response_address=task.poster_address,
        )
        native_currency_transfer_message = get_jetton_transfer_message(
            jetton_wallet_address=user_native_wallet.address,
            recipient_address=job_offer.address.to_string(),
            transfer_fee=to_nano(config.FORWARD_TON_TRANSFER_AMOUNT, "ton"),
            jettons_amount=int(
                config.NATIVE_CURRENCY_PRICE_TO_DEPLOY * 10**native_currency.decimals
            ),
            response_address=task.poster_address,
        )
        response = JobOfferMessageDeployResponseSchema(
            valid_until=int(time.time() + 3600),
            messages=[
                job_offer_deploy_message,
                native_currency_transfer_message,
                task_currency_transfer_message,
            ],
        )
        await self.ton_connect_manager.test_connect_by_task(task, response)
        return response

    async def parse_job_offer(self, result: dict):
        stack = result["stack"]
        (
            title,
            description,
            price,
            owner,
            doer,
            state,
            balance,
            jetton_wallet,
            native_wallet,
            jetton_balance,
            native_balance,
            appeal_address,
            mark,
            review,
        ) = stack
        title = Cell.one_from_boc(b64str_to_bytes(title[1]["bytes"])).bits.get_top_upped_array()
        title = title.decode().split("\x01")[-1]
        result = self.decode_b64(description)
        description = Cell.one_from_boc(
            b64str_to_bytes(description[1]["bytes"])
        ).bits.get_top_upped_array()
        description = description.decode().split("\x01")[-1]
        print(description + result, "DESCRIPTION")
        state = int(state[1], 16)
        print(state, "STATE")
        price = int(price[1], 16)
        print(price, "PRICE")
        jetton_wallet_address = read_address(
            Cell.one_from_boc(b64str_to_bytes(jetton_wallet[1]["bytes"]))
        ).to_string(True, True, True)
        print(jetton_wallet_address, "JETTON MASTER")
        native_wallet_address = read_address(
            Cell.one_from_boc(b64str_to_bytes(native_wallet[1]["bytes"]))
        ).to_string(True, True, True)
        print(native_wallet_address, "MY JETTON WALLET")
        # balance = int(balance[1], 16)
        # print(balance, "BALANCE")
        owner_address = read_address(
            Cell.one_from_boc(b64str_to_bytes(owner[1]["bytes"]))
        ).to_string(True, True, True)
        print(owner_address, "OWNER")
        return {
            "title": title,
            "description": description,
            "price": price,
            "owner": owner_address,
            "doer": doer,
            "state": state,
            "balance": balance,
            "jetton_wallet": jetton_wallet_address,
            "native_wallet": native_wallet_address,
            "jetton_balance": jetton_balance,
            "native_balance": native_balance,
            "appeal_address": appeal_address,
            "mark": mark,
            "review": review,
        }

    def decode_b64(self, data):
        decoded_strings = []

        def recurse(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "b64":
                        decoded_value = base64.b64decode(value).decode("utf-8")
                        decoded_strings.append(decoded_value)
                    else:
                        recurse(value)
            elif isinstance(data, list):
                for item in data:
                    recurse(item)

        recurse(data)
        return "".join(decoded_strings)

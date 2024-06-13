import logging
import time
from typing import Tuple

from pytoniq import LiteClient
from pytoniq_core import Transaction
from pytonlib import TonlibClient
from tonsdk.utils import to_nano
from TonTools.Contracts.Jetton import JettonWallet

from src.apps.category.manager import CategoryManager
from src.apps.currency.manager import CurrencyManager
from src.apps.currency.schemas import CurrencySchema
from src.apps.job_offer.factory import JobOfferFactory
from src.apps.job_offer.job_offer_contract import JobOfferContract
from src.apps.job_offer.schemas import (
    ChooseDoerSchema,
    CompleteJob,
    ConfirmJob,
    GetJob,
    JobOfferMessageSchema,
    RevokeJob,
    TONConnectMessageResponse,
)
from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.manager import TaskManager
from src.apps.tasks.schemas import TaskSchema
from src.apps.TONconnect.manager import TONConnectManager
from src.apps.users.manager import UserManager
from src.apps.users.schemas import UserSchema
from src.apps.utils.exceptions import JsonHTTPException
from src.apps.wallets.manager import WalletManager
from src.apps.wallets.utils import get_jetton_transfer_message
from src.core.config import config
from src.core.utils import require400


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
        job_offer = await self.job_offer_factory.get_job_offer_contract(
            task, native_currency, task_currency
        )
        result = await self.ton_lib_client.raw_run_method(
            job_offer.address.to_string(), "job_data", []
        )
        exit_code = result.get("exit_code")
        require400(
            exit_code == 0 or exit_code == 1, "Can't get job offer data. Possible was not deployed"
        )
        logging.info(f"get_wallet_data result: {result}")
        # await self.get_job_vacancies(job_offer)
        return await job_offer.parse_job_offer(result)

    async def get_job_vacancies(self, job_offer: JobOfferContract):
        result = await self.ton_lib_client.raw_run_method(
            job_offer.address.to_string(), "vacancies", []
        )
        exit_code = result.get("exit_code")
        require400(exit_code == 0, "Can't get job vacancies. Possible was not deployed")
        logging.error(f"get vacancies result: {result}")
        # stack = result.get("stack")
        # b64 = stack[0][1]["object"]["data"]["b64"]
        # bytes_ = stack[0][1]["bytes"]
        # # cell2 = Cell.one_from_boc(b64str_to_bytes(b64))
        # len_ = stack[0][1]["object"]["data"]["len"]
        #
        # # logging.error(f"get vacancies result: {cell}")
        # # slice_ = Slice(c/ell)
        # #
        # # dict_cell = slice_.load_dict()
        # parsed_dict = {}
        # tvm_valuetypes.parse_hashmap(cell2, len_, parsed_dict, bitarray.bitarray())
        # logging.error(f"Dict cell: {parsed_dict}")
        # # boc = cell.to_boc(False)
        # return
        # boc = codecs.decode(b64str_to_bytes(b64).hex(), 'hex')
        # cell = deserialize_boc(boc)
        # len_ = stack[0][1]["object"]["data"]["len"]
        # result = {}
        # # return
        # tvm_valuetypes.parse_hashmap(content.refs[0], len_, result, bitarray.bitarray(''))
        # logging.error(f"get vacancies result: {result}")
        return result

    async def create_deploy_message(self, data: JobOfferMessageSchema):
        task = await self.task_manager.get_task(data.task_id)
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
        await self.check_poster_balance_for_deploy(
            task.poster_address, task.price, task_currency, native_currency
        )
        job_offer = await self.job_offer_factory.get_job_offer_contract(
            task, native_currency, task_currency
        )
        job_offer_address = job_offer.address.to_string()
        job_offer_data = {
            "job_offer_address": job_offer_address,
            "jetton_master_address": task_currency.address,
            "jetton_native_address": native_currency.address,
            "owner": task.poster_address,
            "vacancies": [],
        }
        await self.task_manager.update_task(
            task.task_id,
            {
                "job_offer": job_offer_data,
                "status": TaskStatusEnum.PRE_DEPLOYING,
            },
        )
        job_offer_deploy_message = job_offer.get_deploy_message()
        task_currency_transfer_message = get_jetton_transfer_message(
            jetton_wallet_address=user_task_wallet.address,
            recipient_address=job_offer.address.to_string(),
            transfer_fee=to_nano(config.TON_TRANSFER_AMOUNT, "ton"),
            jettons_amount=job_offer.price,
            response_address=task.poster_address,
            forward_amount=to_nano(config.JETTON_TRANSFER_FORWARD_FEE, "ton"),
        )
        native_currency_transfer_message = get_jetton_transfer_message(
            jetton_wallet_address=user_native_wallet.address,
            recipient_address=job_offer.address.to_string(),
            transfer_fee=to_nano(config.TON_TRANSFER_AMOUNT, "ton"),
            jettons_amount=int(
                config.NATIVE_CURRENCY_PRICE_TO_DEPLOY * 10**native_currency.decimals
            ),
            response_address=task.poster_address,
            forward_amount=to_nano(config.JETTON_TRANSFER_FORWARD_FEE, "ton"),
        )
        response = TONConnectMessageResponse(
            valid_until=int(time.time() + config.TON_CONNECT_VALID_TIME),
            messages=[
                job_offer_deploy_message,
                native_currency_transfer_message,
                task_currency_transfer_message,
            ],
        )
        await self.try_ton_connect(task, response)
        return response

    async def try_ton_connect(self, task, response):
        """This is for testing purpose without application of real transactions"""
        return
        wallet_name = "Tonkeeper"
        connector = self.ton_connect_manager.get_connector(task.poster_id)
        await self.ton_connect_manager.connect_wallet(connector, wallet_name)
        connected = await connector.restore_connection()
        if not connected:
            raise ValueError("Connection failed")
        transaction = response.dict()
        await self.ton_connect_manager.send_transaction(transaction, connector)
        return

    async def get_task_currencies(self, task: TaskSchema) -> Tuple[CurrencySchema, CurrencySchema]:
        native_currency: CurrencySchema = await self.currency_manager.get_native_currency()
        task_currency: CurrencySchema = await self.currency_manager.get(task.currency)
        return native_currency, task_currency

    async def check_poster_balance_for_deploy(
        self,
        poster_address: str,
        task_price: float,
        task_currency: CurrencySchema,
        native_currency: CurrencySchema,
    ):
        await self.task_manager.check_poster_balance_for_deploy(
            poster_address, task_price, task_currency, native_currency
        )

    async def create_get_job_message(self, data: GetJob):
        task: TaskSchema = await self.task_manager.get_task(data.task_id)
        user: UserSchema = await self.user_manager.get_user_by_telegram_id(data.action_by_user)
        require400(task.poster_id != user.telegram_id, "You are the owner of this task")
        require400(user.web3_wallet.address is not None, "You did not connected web3 wallet")
        require400(task.status == TaskStatusEnum.PUBLISHED, "Task is not published")
        nat_curr, task_curr = await self.get_task_currencies(task)
        job_offer = await self.job_offer_factory.get_job_offer_contract(task, nat_curr, task_curr)
        job_offer_get_job_message = job_offer.get_get_job_message()
        response = TONConnectMessageResponse(
            valid_until=int(time.time() + config.TON_CONNECT_VALID_TIME),
            messages=[job_offer_get_job_message],
        )
        await self.try_ton_connect(task, response)
        return response

    async def create_choose_doer_message(self, data: ChooseDoerSchema):
        task: TaskSchema = await self.task_manager.get_task(data.task_id)
        user: UserSchema = await self.user_manager.get_user_by_telegram_id(data.action_by_user)
        require400(task.poster_id == user.telegram_id, "You are not the owner of this task")
        require400(user.web3_wallet.address is not None, "You did not connected web3 wallet")
        require400(task.status == TaskStatusEnum.PUBLISHED, "Task is not published")
        nat_curr, task_curr = await self.get_task_currencies(task)
        job_offer: JobOfferContract = await self.job_offer_factory.get_job_offer_contract(
            task, nat_curr, task_curr
        )
        job_offer_choose_doer_message = job_offer.get_choose_doer_message(data.doer)
        response = TONConnectMessageResponse(
            valid_until=int(time.time() + config.TON_CONNECT_VALID_TIME),
            messages=[job_offer_choose_doer_message],
        )
        await self.try_ton_connect(task, response)
        return response

    async def create_complete_message(self, data: CompleteJob):
        task: TaskSchema = await self.task_manager.get_task(data.task_id)
        user: UserSchema = await self.user_manager.get_user_by_telegram_id(data.action_by_user)
        # require400(task.doer_id == user.telegram_id, "You are not the owner of this task")
        require400(user.web3_wallet.address is not None, "You did not connected web3 wallet")
        # require400(task.status == TaskStatusEnum.PUBLISHED, "Task is not published")
        nat_curr, task_curr = await self.get_task_currencies(task)
        job_offer: JobOfferContract = await self.job_offer_factory.get_job_offer_contract(
            task, nat_curr, task_curr
        )
        job_offer_complete_message = job_offer.get_complete_job_message()
        response = TONConnectMessageResponse(
            valid_until=int(time.time() + config.TON_CONNECT_VALID_TIME),
            messages=[job_offer_complete_message],
        )
        await self.try_ton_connect(task, response)
        return response

    async def create_confirm_message(self, data: ConfirmJob):
        task: TaskSchema = await self.task_manager.get_task(data.task_id)
        user: UserSchema = await self.user_manager.get_user_by_telegram_id(data.action_by_user)
        require400(task.poster_id == user.telegram_id, "You are not the owner of this task")
        require400(user.web3_wallet.address is not None, "You did not connected web3 wallet")
        # TODO check statuses before operation
        # require400(task.status == TaskStatusEnum.PUBLISHED, "Task is not published")
        nat_curr, task_curr = await self.get_task_currencies(task)
        job_offer: JobOfferContract = await self.job_offer_factory.get_job_offer_contract(
            task, nat_curr, task_curr
        )
        job_offer_confirm_message = job_offer.get_confirm_job_message(
            mark=data.mark, review=data.review
        )
        response = TONConnectMessageResponse(
            valid_until=int(time.time() + config.TON_CONNECT_VALID_TIME),
            messages=[job_offer_confirm_message],
        )
        await self.try_ton_connect(task, response)
        return response

    async def create_revoke_message(self, data: RevokeJob):
        task: TaskSchema = await self.task_manager.get_task(data.task_id)
        user: UserSchema = await self.user_manager.get_user_by_telegram_id(data.action_by_user)
        require400(task.poster_id == user.telegram_id, "You are not the owner of this task")
        require400(user.web3_wallet.address is not None, "You did not connected web3 wallet")
        # TODO check statuses before operation
        # require400(task.status == TaskStatusEnum.PUBLISHED, "Task is not published")
        nat_curr, task_curr = await self.get_task_currencies(task)
        job_offer: JobOfferContract = await self.job_offer_factory.get_job_offer_contract(
            task, nat_curr, task_curr
        )
        job_offer_revoke_message = job_offer.get_revoke_message()
        response = TONConnectMessageResponse(
            valid_until=int(time.time() + config.TON_CONNECT_VALID_TIME),
            messages=[job_offer_revoke_message],
        )
        await self.try_ton_connect(task, response)
        return response

    async def process_job_offer_transaction(self, transaction: Transaction, task: TaskSchema):
        pass

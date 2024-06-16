import base64
import logging
import time
from typing import Tuple

from pytoniq import LiteClient
from pytoniq_core import Address, Builder, Cell, HashMap, Transaction
from pytonlib import TonlibClient
from tonsdk.utils import to_nano
from TonTools.Contracts.Jetton import JettonWallet

from src.apps.category.manager import CategoryManager
from src.apps.currency.manager import CurrencyManager
from src.apps.currency.schemas import CurrencySchema
from src.apps.job_offer.enums import JobOfferChainStates, JobOfferOperationCodes
from src.apps.job_offer.factory import JobOfferFactory
from src.apps.job_offer.job_offer_contract import JobOfferContract
from src.apps.job_offer.schemas import (
    ChooseDoerSchema,
    CompleteJob,
    ConfirmJob,
    GetJob,
    JobOfferDataDTO,
    JobOfferMessageSchema,
    RevokeJob,
    TONConnectMessageResponse,
)
from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.manager import TaskManager
from src.apps.tasks.schemas import TaskSchema
from src.apps.TONconnect.manager import TONConnectManager
from src.apps.transaction.schemas import RawTransactionDTO
from src.apps.transaction.service import TransactionService
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
        transaction_service: TransactionService,
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
        self.transaction_service = transaction_service

    async def get_job_offer_chain_state(self, task_id: int) -> JobOfferDataDTO:
        task = await self.task_manager.get_by_task_id(task_id)
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
        # logging.info(f"get_wallet_data result: {result}")
        # await self.get_job_vacancies(job_offer)
        return await job_offer.parse_job_offer(result)

    async def get_job_vacancies(self, job_offer_address: str):
        result = await self.ton_lib_client.raw_run_method(
            address=job_offer_address, method="vacancies", stack_data=[]
        )
        base64_str = result["stack"][0][1]["bytes"]
        byte_data = base64.b64decode(base64_str)
        cell = Cell.one_from_boc(byte_data)
        hash_map = HashMap.from_cell(cell, 267)
        hashmap_cell = hash_map.serialize()

        def key_deserializer(src):
            return Builder().store_bits(src).to_slice().load_address()

        def value_deserializer(src):
            return src.load_bool()

        result = HashMap.parse(
            hashmap_cell.begin_parse(),
            key_length=267,
            key_deserializer=key_deserializer,
            value_deserializer=value_deserializer,
        )

        logging.error(f"get vacancies result: {result}")
        vacancies = []
        for key, value in result.items():
            key: Address
            logging.error(f"key: {key}, value: {value}")
            logging.info(f"key: {key.to_str(False)}, value: {value}")
            owner = await self.user_manager.get_wallet_owner(key.to_str(False))
            if owner is None:
                logging.error(f"Owner not found for address {key.to_str(False)}")
                continue
            vacancies.append(
                {"doer": key.to_str(), "telegram_id": owner.telegram_id, "is_chosen": value}
            )
        return vacancies

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
        await self.task_manager.update_task(
            task.task_id,
            {
                "job_offer": job_offer_data,
                "status": TaskStatusEnum.PRE_DEPLOYING,
            },
        )
        await self.try_ton_connect(task, response)
        return response

    async def try_ton_connect(self, task, response):
        """This is for testing purpose without application of real transactions"""
        # return
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

    async def process_job_offer_transaction(
        self, transaction: Transaction, task: TaskSchema, masterchain_seqno: int
    ):
        parsed_transaction: RawTransactionDTO = await self.transaction_service.parse_transaction(
            transaction
        )
        in_msg = parsed_transaction["in_msg"]

        compute_verdict = False
        action_verdict = False
        if parsed_transaction["compute_phase_code"] is not None and any(
            [
                parsed_transaction["compute_phase_code"] == 0,
                parsed_transaction["compute_phase_code"] == 1,
            ]
        ):
            logging.info(
                f"Transaction {parsed_transaction['hash']} was successful in compute phase"
            )
            compute_verdict = True
        elif parsed_transaction["compute_phase_code"] is None:
            logging.info(f"Transaction {parsed_transaction['hash']} was skipped in compute phase")
            compute_verdict = True
        if parsed_transaction["action_phase_code"] is not None and any(
            [
                parsed_transaction["action_phase_code"] == 0,
                parsed_transaction["action_phase_code"] == 1,
            ]
        ):
            logging.info(f"Transaction {parsed_transaction['hash']} was successful in action phase")
            action_verdict = True
        elif parsed_transaction["action_phase_code"] is None:
            logging.info(f"Transaction {parsed_transaction['hash']} was skipped in action phase")
            action_verdict = True
        if not all([compute_verdict, action_verdict]):
            logging.error(f"Transaction {parsed_transaction['hash']} failed")

        parsed_job_offer_on_chain = await self.get_job_offer_chain_state(task_id=task.task_id)
        logging.info(f"Job offer on chain: {parsed_job_offer_on_chain}")
        chain_state = parsed_job_offer_on_chain["state"]
        logging.info(f"Chain state: {chain_state}")

        match chain_state:
            case JobOfferChainStates.PUBLISHED:
                if in_msg["op_code"] == JobOfferOperationCodes.GET_JOB:
                    vacancies = await self.get_job_vacancies(
                        parsed_transaction["account_address"].to_str()
                    )
                    logging.info(f"Vacancies: {vacancies}")
                    await self.task_manager.update_task(
                        task.task_id, {"job_offer.vacancies": vacancies}
                    )
                await self.task_manager.update_task(
                    task.task_id, {"status": TaskStatusEnum.PUBLISHED}
                )
            case JobOfferChainStates.CLOSED:
                if in_msg["op_code"] == JobOfferOperationCodes.REVOKE:
                    await self.task_manager.update_task(
                        task.task_id, {"status": TaskStatusEnum.REVOKED}
                    )
                elif in_msg["op_code"] == JobOfferOperationCodes.CONFIRM_JOB:
                    await self.task_manager.update_task(
                        task.task_id, {"status": TaskStatusEnum.FINISHED}
                    )
            case JobOfferChainStates.CREATED:
                await self.task_manager.update_task(
                    task.task_id, {"status": TaskStatusEnum.DEPLOYING}
                )
            case JobOfferChainStates.ACCEPTED:
                if in_msg["op_code"] == JobOfferOperationCodes.CHOOSE_DOER:
                    vacancies = await self.get_job_vacancies(
                        parsed_transaction["account_address"].to_str()
                    )
                    logging.info(f"Vacancies: {vacancies}")
                    chosen_doer_address = None
                    chosen_doer_telegram_id = None
                    for vacancy in vacancies:
                        if vacancy.get("is_chosen"):
                            chosen_doer_address = vacancy["doer"]
                            chosen_doer_telegram_id = vacancy["telegram_id"]
                    await self.task_manager.update_task(
                        task.task_id,
                        {
                            "status": TaskStatusEnum.IN_PROGRESS,
                            "job_offer.vacancies": vacancies,
                            "doer_id": chosen_doer_telegram_id,
                            "doer_address": chosen_doer_address,
                        },
                    )
            case JobOfferChainStates.COMPLETED:
                if in_msg["op_code"] == JobOfferOperationCodes.COMPLETE_JOB:
                    await self.task_manager.update_task(
                        task.task_id, {"status": TaskStatusEnum.COMPLETED}
                    )
        logging.info(f"Operation code: {in_msg['op_code']}")
        match in_msg["op_code"]:
            case JobOfferOperationCodes.DEPLOY:
                logging.info("Deploy operation")
                # TODO push notification to poster
            case JobOfferOperationCodes.REVOKE:
                logging.info("Revoke operation")
            case JobOfferOperationCodes.GET_JOB:
                logging.info("Get job operation")
                # TODO push notification to poster
            case JobOfferOperationCodes.COMPLETE_JOB:
                logging.info("Complete job operation")
                # TODO push notification to poster
            case JobOfferOperationCodes.CONFIRM_JOB:
                logging.info("Confirm job operation")
                # TODO push notification to doer
            case JobOfferOperationCodes.APPEAL:
                logging.error("Appeal not implemented")
            case JobOfferOperationCodes.REVOKE_APPEAL:
                logging.error("Revoke appeal not implemented")
            case JobOfferOperationCodes.CONFIRM_APPEAL:
                logging.error("Confirm appeal not implemented")
            case JobOfferOperationCodes.CHOOSE_DOER:
                logging.info("Choose doer operation")
                # TODO push notification to doer
            case JobOfferOperationCodes.TAKE_WALLET_ADDRESS:
                logging.info("Take wallet address operation")
            case _:
                logging.error("Unknown operation code")

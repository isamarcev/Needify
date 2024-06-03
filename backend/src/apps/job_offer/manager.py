import time

from tonsdk.contract.token.ft import JettonWallet as TonSDKJettonWallet
from tonsdk.utils import to_nano
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
    ):
        self.task_manager = task_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.currency_manager = currency_manager
        self.user_manager = user_manager
        self.job_offer_factory = job_offer_factory
        self.ton_connect_manager = ton_connect_manager

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
        # task_currency_transfer_message = tonsdk_wallet.create_transfer_body(
        #     to_address=job_offer.address,
        #     jetton_amount=job_offer.price,
        #     forward_amount=to_nano(config.FORWARD_TON_TRANSFER_AMOUNT, "ton")
        # )
        # int_native_amount = int(config.NATIVE_CURRENCY_PRICE_TO_DEPLOY * 10 ** native_currency.decimals)
        # native_currency_transfer_message = tonsdk_wallet.create_transfer_body(
        #     to_address=job_offer.address,
        #     jetton_amount=int_native_amount,
        #     forward_amount=to_nano(config.FORWARD_TON_TRANSFER_AMOUNT, "ton")
        # )
        response = JobOfferMessageDeployResponseSchema(
            valid_until=int(time.time() + 3600),
            messages=[
                job_offer_deploy_message,
                # native_currency_transfer_message,
                # task_currency_transfer_message
            ],
        )
        await self.ton_connect_manager.test_connect_by_task(task, response)
        return response

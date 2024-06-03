import logging
from abc import ABC, abstractmethod

from pytonlib import TonlibClient
from tonsdk.utils import to_nano
from TonTools.Contracts.Jetton import Jetton, JettonWallet
from TonTools.Providers.TonCenterClient import GetMethodError, TonCenterClient

from src.apps.currency.custom_minter import jUSDTMinter, jUSDTWallet
from src.apps.currency.exceptions import (
    CurrencyAddressNotFoundJsonException,
    CurrencyNotFoundJsonException,
)
from src.apps.currency.jetton_metadata import NEED_JETTON_METADATA
from src.apps.currency.mint_bodies import create_state_init_jetton, increase_supply
from src.apps.currency.schemas import CreateCurrencySchema, CurrencySchema, MintTokenSchema
from src.apps.utils.exceptions import JsonHTTPException
from src.apps.utils.wallet import get_sdk_wallet_by_mnemonic, get_wallet_info_by_mnemonic
from src.core.config import config
from src.core.repository import BaseMongoRepository

logger = logging.getLogger("root")


class BaseCurrencyManager(ABC):
    @abstractmethod
    async def get_currencies(self) -> list[CurrencySchema]:
        pass


class CurrencyManager(BaseCurrencyManager):
    def __init__(
        self,
        ton_lib_client: TonlibClient,
        repository: BaseMongoRepository,
        ton_center_client: TonCenterClient,
    ):
        self.ton_lib_client = ton_lib_client
        self.ton_center_client = ton_center_client
        self.repository = repository

    async def get_currencies(self) -> list[CurrencySchema]:
        native_currency = await self.get_native_currency()
        # exclude native currency
        currencies = await self.repository.get_list(
            by_filter={"address": {"$ne": native_currency.address}}
        )
        return [
            CurrencySchema(**currency) for currency in currencies if currency != native_currency
        ]

    async def get(self, symbol: str, raise_if_not_exist: bool = True) -> CurrencySchema | None:
        currency = await self.repository.get_by_filter({"symbol": symbol})
        if not currency and raise_if_not_exist:
            raise CurrencyNotFoundJsonException(symbol)
        return CurrencySchema(**currency) if currency else None

    async def get_jetton_master(self, jetton_master_address: str):
        return Jetton(data=jetton_master_address, provider=self.ton_center_client)

    async def get_jetton_wallet(
        self, jetton_master_address: str, owner: str | None = None
    ) -> JettonWallet:
        try:
            if not owner:
                owner = config.HD_WALLET_ADDRESS
            res = await self.ton_center_client.get_jetton_wallet_address(
                jetton_master_address, owner
            )
            wallet = await self.ton_center_client.get_jetton_wallet(res)
        except GetMethodError as e:
            logger.error(f"Error: {e}")
            raise JsonHTTPException(
                status_code=404,
                error_description=f"Jetton Wallet for {jetton_master_address} not found",
                error_name="NotFound",
            ) from e
        return wallet

    async def is_enough_balance(self, currency: CurrencySchema, owner: str, amount: int):
        wallet = await self.get_jetton_wallet(currency.address, owner)
        logger.info(f"Wallet info: {wallet}. Balance: {wallet.balance} Amount: {amount}")
        return wallet.balance >= amount

    async def create_currency(self, data: CreateCurrencySchema) -> CreateCurrencySchema:
        raise NotImplementedError()

    async def get_currency_by_address(self, address: str, raise_if_not_exist: bool = True):
        currency = await self.repository.get_by_filter({"address": address})
        if not currency and raise_if_not_exist:
            raise CurrencyAddressNotFoundJsonException(address)
        return CurrencySchema(**currency)

    async def get_native_currency(self):
        currency = await self.repository.get_by_filter({"address": NEED_JETTON_METADATA["address"]})
        logger.info(f"Native currency exist: {bool(currency)}")
        if not currency:
            currency = await self.create_currency(
                CreateCurrencySchema(
                    address=NEED_JETTON_METADATA["address"],
                )
            )
        return CurrencySchema(**currency)

    async def get_seqno(self, address: str):
        data = await self.ton_lib_client.raw_run_method(
            method="seqno", stack_data=[], address=address
        )
        return int(data["stack"][0][1], 16)

    async def deploy_jUSDT_minter(self):
        state_init, jetton_address = create_state_init_jetton(
            minter_class=jUSDTMinter, wallet_class=jUSDTWallet
        )
        hd_wallet_info = get_wallet_info_by_mnemonic(
            config.hd_wallet_mnemonic_list,
            config.WORKCHAIN,
            is_testnet=config.IS_TESTNET,
        )
        seqno = await self.get_seqno(hd_wallet_info.get("wallet_address"))
        wallet = hd_wallet_info.get("wallet")
        query = wallet.create_transfer_message(
            to_addr=jetton_address,
            amount=to_nano(config.AMOUNT_TON_TO_DEPLOY, "ton"),
            seqno=seqno,
            state_init=state_init,
        )
        result = await self.ton_lib_client.raw_send_message(query["message"].to_boc(False))
        return result

    async def mint_tokens(self, mint_data: MintTokenSchema):
        jetton_master = await self.get_currency_by_address(mint_data.address)
        if jetton_master is None or not jetton_master.is_active:
            raise CurrencyAddressNotFoundJsonException(mint_data.address)
        # if jetton_master.symbol == jUSDT_content.get("symbol"):
        #     body = increase_supply(
        #         to_nano(mint_data.amount, "ton"),
        #         destination=mint_data.destination,
        #         minter_class=jUSDTMinter,
        #         wallet_class=jUSDTWallet,
        #     )
        #     state_init, jetton_address = create_state_init_jetton(
        #         minter_class=jUSDTMinter, wallet_class=jUSDTWallet
        #     )
        # elif jetton_master.symbol == config.NATIVE_SYMBOL:
        body = increase_supply(to_nano(mint_data.amount, "ton"), destination=mint_data.destination)
        state_init, jetton_address = create_state_init_jetton()
        # else:
        #     raise CurrencyAddressNotFoundJsonException(mint_data.address)
        seqno = await self.get_seqno(config.HD_WALLET_ADDRESS)
        wallet = get_sdk_wallet_by_mnemonic(
            config.hd_wallet_mnemonic_list,
            config.WORKCHAIN,
            is_testnet=config.IS_TESTNET,
        )
        query = wallet.create_transfer_message(
            to_addr=jetton_address,
            amount=to_nano(config.AMOUNT_TON_TO_DEPLOY, "ton"),
            seqno=seqno,
            payload=body,
        )
        result = await self.ton_lib_client.raw_send_message(query["message"].to_boc(False))
        return result

    # async def burn_tokens(self, amount_to_burn: int):
    #     body = JettonWallet().create_burn_body(
    #         jetton_amount=to_nano(amount_to_burn, "ton")
    #     )
    #     state_init, jetton_address = create_state_init_jetton()
    #     seqno = await self.get_seqno(config.HD_WALLET_ADDRESS)
    #     wallet = get_sdk_wallet_by_mnemonic(
    #         config.hd_wallet_mnemonic_list,
    #         config.WORKCHAIN,
    #         is_testnet=config.IS_TESTNET,
    #     )
    #     query = wallet.create_transfer_message(
    #         to_addr=jetton_address,
    #         amount=to_nano(config.AMOUNT_TON_TO_DEPLOY, "ton"),
    #         seqno=seqno,
    #         payload=body,
    #     )
    #     result = await self.lts_client.raw_send_message(query["message"].to_boc(False))
    #     return result

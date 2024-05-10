from abc import ABC

from tonsdk.contract.token.ft import JettonWallet
from tonsdk.utils import to_nano

from src.apps.currency.exceptions import (
    CurrencyNotFoundJsonException,
    CurrencyValidationJsonException,
)
from src.apps.currency.mint_bodies import create_state_init_jetton, increase_supply
from src.apps.currency.schemas import (
    CreateCurrencySchema,
    CurrencySchema,
    MintTokenSchema,
)
from src.apps.utils.wallet import (
    get_sdk_wallet_by_mnemonic,
    get_wallet_info_by_mnemonic,
)
from src.core.config import config
from src.core.repository import BaseMongoRepository


class BaseCurrencyManager(ABC):
    pass


class CurrencyManager(BaseCurrencyManager):
    def __init__(self, lts_client, repository: BaseMongoRepository):
        self.lts_client = lts_client
        self.repository = repository

    async def get_currencies(self) -> list[CurrencySchema]:
        currencies = await self.repository.get_list()
        return [CurrencySchema(**currency) for currency in currencies]

    async def get(
        self, symbol: str, raise_if_not_exist: bool = True
    ) -> CurrencySchema | None:
        currency = await self.repository.get_by_filter({"symbol": symbol})
        if not currency and raise_if_not_exist:
            raise CurrencyNotFoundJsonException(symbol)
        return CreateCurrencySchema(**currency) if currency else None

    async def create_currency(self, data: CreateCurrencySchema) -> CreateCurrencySchema:
        if await self.get(data.symbol, raise_if_not_exist=False):
            raise CurrencyValidationJsonException(
                f"Currency {data.symbol} already exists"
            )
        elif await self.repository.get_by_filter(
            {"jetton_master_address": data.jetton_master_address}
        ):
            raise CurrencyValidationJsonException(
                f"Currency with jetton_master_address {data.jetton_master_address} already exists"
            )
        currency = await self.repository.create(data.dict())
        return CreateCurrencySchema(**currency)

    async def get_seqno(self, address: str):
        data = await self.lts_client.raw_run_method(
            method="seqno", stack_data=[], address=address
        )
        return int(data["stack"][0][1], 16)

    async def deploy_minter(self):
        state_init, jetton_address = create_state_init_jetton()
        # client = await get_lite_server_client()
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
        result = await self.lts_client.raw_send_message(query["message"].to_boc(False))
        return result

    async def mint_tokens(self, mint_data: MintTokenSchema):
        body = increase_supply(mint_data.amount, destination=mint_data.destination)
        state_init, jetton_address = create_state_init_jetton()
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
        result = await self.lts_client.raw_send_message(query["message"].to_boc(False))
        return result

    async def burn_tokens(self, amount_to_burn: int):
        body = JettonWallet().create_burn_body(
            jetton_amount=to_nano(amount_to_burn, "ton")
        )
        state_init, jetton_address = create_state_init_jetton()
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
        result = await self.lts_client.raw_send_message(query["message"].to_boc(False))
        return result

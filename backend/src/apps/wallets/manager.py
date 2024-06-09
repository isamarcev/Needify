from pytoniq import LiteClient
from TonTools.Contracts.Jetton import Jetton, JettonWallet
from TonTools.Contracts.Wallet import Wallet
from TonTools.Providers.TonCenterClient import TonCenterClient

from src.apps.currency.schemas import CurrencySchema
from src.apps.wallets.events import WalletTopicsEnum
from src.apps.wallets.exceptions import (
    DepositWalletNotFoundException,
    DepositWalletValidationJsonException,
)
from src.apps.wallets.schemas import DepositWalletSchema
from src.core.producer import KafkaProducer
from src.core.repository import BaseMongoRepository


class WalletManager:
    WALLET_VERSION = "v4r2"

    def __init__(
        self,
        repository: BaseMongoRepository,
        main_wallet_mnemonics: list[str],
        main_wallet_address: str,
        provider: TonCenterClient,
        liteserver_client: LiteClient,
        producer: KafkaProducer,
    ):
        self.repository = repository
        self.main_wallet_mnemonics = main_wallet_mnemonics
        self.main_wallet_address = main_wallet_address
        self.provider = provider
        self.liteserver_client = liteserver_client
        self.producer = producer

    async def get_deposit_wallets(self) -> list[DepositWalletSchema]:
        wallets = await self.repository.get_list()
        return [DepositWalletSchema(**wallet) for wallet in wallets]

    async def test_(self):
        await self.producer.publish_message(
            WalletTopicsEnum.FOUNDED_DEPOSIT_WALLET, {"test": "test"}
        )

    def get_jetton_master(self, jetton_master_address: str):
        return Jetton(data=jetton_master_address, provider=self.provider)

    # async def get_wallet(self, address: str, mnemonics: list = None, version="v4r2") -> Wallet:
    #     return Wallet(
    #         provider=self.provider,
    #         address=address,
    #         mnemonics=mnemonics,
    #         version=version,
    #     )

    async def is_enough_jettons_to_transfer(
        self, currency: CurrencySchema, source_address: str, amount: float
    ):
        jetton_wallet = await self.get_jetton_wallet(currency.address, source_address)
        balance = await jetton_wallet.get_balance()  # nanoTons
        amount = amount * 10**currency.decimals
        return balance >= amount

    async def get_jetton_wallet(self, jetton_master_address: str, address: str) -> JettonWallet:
        jetton_master = self.get_jetton_master(jetton_master_address)
        jetton_wallet = await jetton_master.get_jetton_wallet(address)
        return jetton_wallet

    async def insert_deposit_wallet(
        self, deposit_wallet: DepositWalletSchema
    ) -> DepositWalletSchema:
        if await self.get_deposit_wallet(deposit_wallet.address, raise_if_not_exist=False):
            raise DepositWalletValidationJsonException(
                f"Deposit wallet {deposit_wallet.address} already exists"
            )
        await self.repository.create(deposit_wallet.dict())
        return deposit_wallet

    async def get_deposit_wallet(
        self, address: str, raise_if_not_exist: bool = True
    ) -> DepositWalletSchema:
        wallet = await self.repository.get_by_filter({"address": address})
        if not wallet and raise_if_not_exist:
            raise DepositWalletNotFoundException(address)
        return DepositWalletSchema(**wallet) if wallet else None

    @staticmethod
    def get_wallet(wallet_mnemonics: list[str], provider: TonCenterClient) -> Wallet:
        return Wallet(
            mnemonics=wallet_mnemonics,
            provider=provider,
            version=WalletManager.WALLET_VERSION,
        )

    async def get_account_balance(self, address: str) -> int:
        account_state = await self.liteserver_client.get_account_state(address)
        return account_state

    async def handle_wallet_created(self, message: dict) -> None:
        print(f"Wallet created: {message}")

from tonsdk.crypto import mnemonic_to_hd_seed
from tonsdk.crypto.hd import derive_mnemonics_path
from TonTools.Contracts.Wallet import Wallet
from TonTools.Providers.TonCenterClient import TonCenterClient

from src.apps.wallets.exceptions import (
    DepositWalletNotFoundException,
    DepositWalletValidationJsonException,
)
from src.apps.wallets.schemas import DepositWalletSchema
from src.core.repository import BaseMongoRepository


class WalletManager:

    WALLET_VERSION = "v4r2"

    def __init__(
        self,
        repository: BaseMongoRepository,
        main_wallet_mnemonics: list[str],
        main_wallet_address: str,
        provider: TonCenterClient,
    ):
        self.repository = repository
        self.main_wallet_mnemonics = main_wallet_mnemonics
        self.main_wallet_address = main_wallet_address
        self.provider = provider

    async def get_deposit_wallets(self) -> list[DepositWalletSchema]:
        wallets = await self.repository.get_list()
        return [DepositWalletSchema(**wallet) for wallet in wallets]

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

    async def get_deposit_wallet_object(self, task_id: int) -> Wallet:
        deposit_wallet = await self.generate_deposit_wallet(task_id)
        return self.get_wallet(deposit_wallet.mnemonic, self.provider)

    async def generate_deposit_wallet(self, index: int) -> DepositWalletSchema:
        path = self.get_path(index)
        deposit_wallet_mnemonic = derive_mnemonics_path(
            mnemonic_to_hd_seed(self.main_wallet_mnemonics), path
        )
        deposit_wallet = self.get_wallet(deposit_wallet_mnemonic, self.provider)
        deposit_wallet_schema = DepositWalletSchema(
            task_id=index,
            address=deposit_wallet.address,
            hd_wallet_address=self.main_wallet_address,
        )
        return deposit_wallet_schema

    async def create_deposit_wallet_for_task(self, task_id: int) -> DepositWalletSchema:
        deposit_wallet_schema = await self.generate_deposit_wallet(task_id)
        await self.insert_deposit_wallet(deposit_wallet_schema)
        return await self.generate_deposit_wallet(task_id)

    async def get_main_wallet_object(self) -> Wallet:
        return self.get_wallet(self.main_wallet_mnemonics, self.provider)

    @staticmethod
    def get_path(index: int) -> list:
        return [0, 0, index]

    @staticmethod
    def get_wallet(wallet_mnemonics: list[str], provider: TonCenterClient) -> Wallet:
        return Wallet(
            mnemonics=wallet_mnemonics, provider=provider, version=WalletManager.WALLET_VERSION
        )

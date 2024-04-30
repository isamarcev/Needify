from TonTools.Contracts.Wallet import Wallet

from src.apps.wallets.manager import WalletManager
from src.core.config import config
from src.core.database import async_mongo
from src.core.provider import get_tonsdk_center_client
from src.apps.wallets.jetton_manager import JettonManager
from src.core.repository import BaseMongoRepository


async def get_main_wallet() -> Wallet:
    provider = await get_tonsdk_center_client()
    wallet = Wallet(mnemonics=config.hd_wallet_mnemonic_list, provider=provider)
    return wallet


async def get_jetton_manager() -> JettonManager:
    manager = JettonManager(ton_center_client=await get_tonsdk_center_client())
    return manager


async def get_wallet_repository():
    repository = BaseMongoRepository(
        mongo_client=async_mongo,
        collection_name="wallets"
    )
    return repository


async def get_wallet_manager() -> WalletManager:
    return WalletManager(
        repository=await get_wallet_repository(),
        main_wallet_mnemonics=config.hd_wallet_mnemonic_list,
        main_wallet_address=config.HD_WALLET_ADDRESS,
        provider=await get_tonsdk_center_client()
    )

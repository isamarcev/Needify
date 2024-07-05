from pytoniq import LiteClient, WalletV4R2
from tonsdk.contract.wallet import WalletContract, Wallets, WalletVersionEnum


def get_wallet_info_by_mnemonic(
    mnemonics: list[str],
    workchain: int,
    version: WalletVersionEnum = WalletVersionEnum.v4r2,
    is_testnet: bool = False,
) -> dict:
    mnemonics, pub_k, priv_key, wallet = Wallets.from_mnemonics(
        mnemonics=mnemonics, workchain=workchain, version=version
    )
    wallet_address = wallet.address.to_string(True, True, True, is_testnet)
    return {
        "mnemonics": mnemonics,
        "public_key": pub_k,
        "private_key": priv_key,
        "wallet": wallet,
        "wallet_address": wallet_address,
    }


def get_sdk_wallet_by_mnemonic(
    mnemonics: list[str],
    workchain: int,
    version: WalletVersionEnum = WalletVersionEnum.v4r2,
    is_testnet: bool = False,
) -> WalletContract:
    wallet_info = get_wallet_info_by_mnemonic(
        mnemonics=mnemonics, workchain=workchain, version=version, is_testnet=is_testnet
    )
    return wallet_info.get("wallet")


async def get_pytoniq_wallet_by_mnemonic(
    mnemonics: list[str],
    workchain: int,
    lite_client: LiteClient,
) -> WalletV4R2:
    wallet = await WalletV4R2.from_mnemonic(lite_client, mnemonics=mnemonics, wc=workchain)
    return wallet

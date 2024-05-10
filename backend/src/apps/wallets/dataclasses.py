from dataclasses import dataclass

from TonTools.Contracts.Wallet import Wallet
from TonTools.Providers.TonCenterClient import TonCenterClient


@dataclass
class MainWallet:
    VERSION = "v4r2"

    mnemonic: list[str]

    @classmethod
    def create(cls, mnemonic: list[str], provider: TonCenterClient) -> Wallet:
        return Wallet(mnemonics=mnemonic, provider=provider, version=cls.VERSION)

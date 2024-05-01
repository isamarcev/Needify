from TonTools import TonCenterClient, Wallet


class JettonManager:
    def __init__(self, ton_center_client: TonCenterClient):
        self.ton_center_client = ton_center_client

    @classmethod
    async def transfer(
        cls, wallet: Wallet, destination_address: str, amount: int, jetton_master_address: str
    ):
        result = await wallet.transfer_jetton(
            destination_address=destination_address,
            jetton_master_address=jetton_master_address,
            jettons_amount=amount,
        )
        return result

    async def get_jetton_address(self):
        return await self.ton_center_client.get_jetton_address()


class JettonWalletManager:
    pass

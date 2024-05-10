from pydantic import BaseModel


class DepositWalletSchema(BaseModel):
    address: str
    balance: int
    task_id: int
    hd_wallet_address: str


class JettonTransferSchema(BaseModel):
    destination_address: str
    amount: int

from pydantic import BaseModel


class ConnectDepositSchema(BaseModel):

    action_by_user_id: int
    jetton_wallet_address: str
    recipient_address: str
    transfer_fee: float
    jettons_amount: float
    wallet_name: str

from pydantic import BaseModel, PositiveInt


class CurrencySchema(BaseModel):
    # supply: int
    jetton_master_address: str
    decimals: int
    symbol: str
    name: str
    # image: str
    # token_supply: float
    is_active: bool


class CreateCurrencySchema(BaseModel):
    jetton_master_address: str


class MintTokenSchema(BaseModel):
    jetton_master_address: str
    amount: PositiveInt
    destination: str


class BurnDataSchema(BaseModel):
    amount: PositiveInt

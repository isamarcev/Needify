from pydantic import BaseModel, PositiveInt


class CurrencySchema(BaseModel):
    name: str
    symbol: str
    decimals: PositiveInt
    jetton_master_address: str
    is_active: bool


class CreateCurrencySchema(BaseModel):
    name: str
    symbol: str
    decimals: PositiveInt
    jetton_master_address: str
    is_active: bool = True


class MintTokenSchema(BaseModel):
    amount: PositiveInt
    destination: str


class BurnDataSchema(BaseModel):
    amount: PositiveInt

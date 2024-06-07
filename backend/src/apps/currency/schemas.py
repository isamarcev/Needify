from pydantic import BaseModel, PositiveInt


class CurrencySchema(BaseModel):
    address: str
    decimals: int
    symbol: str
    name: str
    image: str
    is_active: bool = False
    description: str


class CreateCurrencySchema(BaseModel):
    address: str


class MintTokenSchema(BaseModel):
    address: str
    amount: PositiveInt
    destination: str


class BurnDataSchema(BaseModel):
    amount: PositiveInt

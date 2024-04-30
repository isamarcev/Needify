from fastapi import APIRouter, Depends

from src.apps.currency.dependencies import get_currency_manager
from src.apps.currency.manager import CurrencyManager
from src.apps.currency.schemas import MintTokenSchema, BurnDataSchema, CreateCurrencySchema

currency_router = APIRouter()


@currency_router.get("/")
async def get_list_currencies(currency_manager: CurrencyManager = Depends(get_currency_manager)):
    result = await currency_manager.get_currencies()
    return result


@currency_router.post("/")
async def create_currency(
        data: CreateCurrencySchema,
        currency_manager: CurrencyManager = Depends(get_currency_manager),
):
    result = await currency_manager.create_currency(data)
    return {"message": result}


@currency_router.get("/deploy-minter")
async def deploy_minter(currency_manager: CurrencyManager = Depends(get_currency_manager)):
    result = await currency_manager.deploy_minter()
    return {"message": result}


@currency_router.post("/mint-tokens")
async def mint_tokens(
        mint_data: MintTokenSchema,
        currency_manager: CurrencyManager = Depends(get_currency_manager),
):
    result = await currency_manager.mint_tokens(mint_data)
    return {"message": result}


@currency_router.post("/burn-tokens")
async def burn_tokens(
        burn_data: BurnDataSchema,
        currency_manager: CurrencyManager = Depends(get_currency_manager),
):
    result = await currency_manager.burn_tokens(burn_data.amount)
    return {"message": result}




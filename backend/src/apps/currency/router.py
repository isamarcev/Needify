from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.currency.dependencies import CurrencyContainer
from src.apps.currency.manager import CurrencyManager
from src.apps.currency.schemas import MintTokenSchema, BurnDataSchema, CreateCurrencySchema

currency_router = APIRouter()


@currency_router.get("/")
@inject
async def get_list_currencies(currency_manager: CurrencyManager = Depends(Provide[CurrencyContainer.currency_manager])):
    result = await currency_manager.get_currencies()
    return result


@currency_router.post("/")
@inject
async def create_currency(
        data: CreateCurrencySchema,
        currency_manager: CurrencyManager = Depends(Provide[CurrencyContainer.currency_manager]),
):
    result = await currency_manager.create_currency(data)
    return {"message": result}


@currency_router.get("/deploy-minter")
@inject
async def deploy_minter(currency_manager: CurrencyManager = Depends(Provide[CurrencyContainer.currency_manager])):
    result = await currency_manager.deploy_minter()
    return {"message": result}


@currency_router.post("/mint-tokens")
@inject
async def mint_tokens(
        mint_data: MintTokenSchema,
        currency_manager: CurrencyManager = Depends(Provide[CurrencyContainer.currency_manager]),
):
    result = await currency_manager.mint_tokens(mint_data)
    return {"message": result}


@currency_router.post("/burn-tokens")
@inject
async def burn_tokens(
        burn_data: BurnDataSchema,
        currency_manager: CurrencyManager = Depends(Provide[CurrencyContainer.currency_manager]),
):
    result = await currency_manager.burn_tokens(burn_data.amount)
    return {"message": result}




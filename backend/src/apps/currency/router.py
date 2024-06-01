from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.currency.dependencies import CurrencyContainer
from src.apps.currency.manager import CurrencyManager
from src.apps.currency.schemas import BurnDataSchema, CreateCurrencySchema, MintTokenSchema, \
    CurrencySchema

currency_router = APIRouter()


# @currency_router.get("/try-deploy-jUSDT")
# @inject
# async def get_master_data(
#     address: str,
#     currency_manager: CurrencyManager = Depends(
#         Provide[CurrencyContainer.currency_manager]
#     ),
# ):
#     result = await currency_manager.deploy_jUSDT_minter()
#     # await result.update()
#
#     return result
#
#
# @currency_router.post("/mint")
# @inject
# async def mint_(
#     schema: MintTokenSchema,
#     currency_manager: CurrencyManager = Depends(
#         Provide[CurrencyContainer.currency_manager]
#     ),
# ):
#     result = await currency_manager.mint_tokens(schema)
#     return result



@currency_router.get("/",
                     response_model=list[CurrencySchema],
                     )
@inject
async def get_list_currencies(
    currency_manager: CurrencyManager = Depends(
        Provide[CurrencyContainer.currency_manager]
    ),
):
    result = await currency_manager.get_currencies()
    return result


@currency_router.get("/native-currency",
                     response_model=CurrencySchema,
                     )
@inject
async def get_native_currency(
    currency_manager: CurrencyManager = Depends(
        Provide[CurrencyContainer.currency_manager]
    ),
):
    result = await currency_manager.get_native_currency()
    return result



# @currency_router.post("/")
# @inject
# async def create_currency(
#     data: CreateCurrencySchema,
#     currency_manager: CurrencyManager = Depends(
#         Provide[CurrencyContainer.currency_manager]
#     ),
# ):
#     result = await currency_manager.create_currency(data)
#     return {"message": result}
#
#
# @currency_router.get("/deploy-minter")
# @inject
# async def deploy_minter(
#     currency_manager: CurrencyManager = Depends(
#         Provide[CurrencyContainer.currency_manager]
#     ),
# ):
#     result = await currency_manager.deploy_minter()
#     return {"message": result}
#
#
# @currency_router.post("/mint-tokens")
# @inject
# async def mint_tokens(
#     mint_data: MintTokenSchema,
#     currency_manager: CurrencyManager = Depends(
#         Provide[CurrencyContainer.currency_manager]
#     ),
# ):
#     result = await currency_manager.mint_tokens(mint_data)
#     return {"message": result}
#
#
# @currency_router.post("/burn-tokens")
# @inject
# async def burn_tokens(
#     burn_data: BurnDataSchema,
#     currency_manager: CurrencyManager = Depends(
#         Provide[CurrencyContainer.currency_manager]
#     ),
# ):
#     result = await currency_manager.burn_tokens(burn_data.amount)
#     return {"message": result}
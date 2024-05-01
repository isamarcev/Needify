from fastapi import FastAPI, APIRouter, Depends

from src.apps.category.dependencies import CategoryContainer
from src.apps.currency.dependencies import CurrencyContainer
from src.apps.tasks.dependencies import TaskContainer
from src.apps.users.dependencies import UserContainer
from src.apps.wallets.dependencies import WalletContainer
from src.core.config import config
from src.core.database import setup_database, async_mongo
from src.core.middlewares import setup_middlewares
from src.core.router import v1_router

FASTAPI_CONFIG = {
    "title": "The Open Times",
    "version": "1.0.0",
    "description": "This is a service for The Open TImes project",
}


def app_factory():
    fastapi_app = FastAPI(
        **FASTAPI_CONFIG,
    )
    main_router = APIRouter()
    main_router.include_router(v1_router)
    fastapi_app.include_router(main_router)
    setup_middlewares(fastapi_app)
    return fastapi_app


app = app_factory()


async def setup_containers():
    user_container = UserContainer()
    user_container.config.from_pydantic(settings=config)

    currency_container = CurrencyContainer()
    currency_container.config.from_pydantic(settings=config)

    category_container = CategoryContainer()
    category_container.config.from_pydantic(settings=config)

    wallet_container = WalletContainer()
    wallet_container.config.from_pydantic(settings=config)

    task_container = TaskContainer(
        category_manager=category_container.category_manager.provided,
        wallet_manager=wallet_container.wallet_manager.provided

    )
    task_container.config.from_pydantic(settings=config)


@app.on_event("startup")
async def startup_event():
    await setup_containers()
    await setup_database(async_mongo)


@app.get("/")
async def root():
    return {"message": "Hello World"}
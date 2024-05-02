import asyncio

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, FastAPI

from src.core.config import config
from src.core.database import async_mongo, setup_database
from src.core.dependencies import CoreContainer
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




async def setup_containers():

    core_container = CoreContainer()
    core_container.config.from_pydantic(settings=config)
    app.core_container = core_container

app = app_factory()

@app.on_event("startup")
async def startup_event():
    await setup_containers()
    core_container = app.core_container
    message_hub = core_container.message_hub()
    asyncio.create_task(message_hub.consume())

    await setup_database(async_mongo)


@app.get("/")
@inject
async def root():
    return {"message": "Hello World"}

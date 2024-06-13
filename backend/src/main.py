import asyncio
import json
import logging

from dependency_injector.wiring import inject
from fastapi import APIRouter, FastAPI
from pytoniq import LiteClient

from src.apps.scanner.service import BlockScanner
from src.core.config import config
from src.core.database import async_mongo, setup_database
from src.core.dependencies import CoreContainer
from src.core.logger_settings import setup_logging
from src.core.middlewares import setup_middlewares
from src.core.router import v1_router

FASTAPI_CONFIG = {
    "title": "Needify",
    "version": "1.0.0",
    "description": "This is a service for Needify app",
}

setup_logging()

logger = logging.getLogger("root")
fastapi_app = FastAPI(
    **FASTAPI_CONFIG,
)


async def setup_containers():
    core_container = CoreContainer()
    core_container.config.from_pydantic(settings=config)
    fastapi_app.core_container = core_container


def app_factory():
    main_router = APIRouter()
    main_router.include_router(v1_router)
    fastapi_app.include_router(main_router)
    setup_middlewares(fastapi_app)
    return fastapi_app


@fastapi_app.on_event("startup")
async def startup_event():
    await setup_containers()
    core_container = fastapi_app.core_container
    # core_container.ton_lib_client()

    lite_client: LiteClient = core_container.lite_client()
    await lite_client.connect()

    message_hub = core_container.message_hub()
    asyncio.create_task(message_hub.consume())
    openapi_data = fastapi_app.openapi()
    # Change "openapi.json" to desired filename
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)

    await setup_database(async_mongo)
    scanner_service: BlockScanner = await core_container.scanner_service()
    asyncio.create_task(scanner_service.run())


@fastapi_app.on_event("shutdown")
async def shutdown_event():
    core_container = fastapi_app.core_container
    lite_client: LiteClient = core_container.lite_client()
    await lite_client.close()


@fastapi_app.get("/")
@inject
async def root():
    logger.info("Hello World")
    logger.warning("Hello World")
    logger.error("Hello World")

    return {"message": "Hello World"}


app = app_factory()

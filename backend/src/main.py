import asyncio
import logging

from dependency_injector.wiring import inject
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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

def create_readable_error_detail(errors):
    readable_errors = []
    for error in errors:
        loc = " -> ".join(error['loc'])
        msg = error['msg']
        error_type = error['type']
        readable_errors.append(f"Field '{loc}' error: {msg} (type: {error_type})")
    return readable_errors

@fastapi_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    readable_errors = create_readable_error_detail(exc.errors())
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "name": "VALIDATION_ERROR",
                "description": "Validation failed for one or more fields.",
                "code": 400,
                "meta": {
                    "errors": readable_errors
                }
            }
        }
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
    config = core_container.config
    if config.UPDATE_LAST_SCANNED_BLOCK:
        logging.info("Resetting last scanned block")
        local_storage = core_container.local_storage()
        await local_storage.reset_last_scanned_block()

    lite_client: LiteClient = core_container.lite_client()
    await lite_client.connect()

    # setup categories
    category_manager = core_container.category_container.category_manager()
    await category_manager.on_startup()

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

from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from starlette.requests import Request

from src.apps.utils.exceptions import JsonHTTPException


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        return JsonHTTPException(
            status_code=exc.status_code,
            error_name="HTTP_EXCEPTION",
            error_description=HTTPStatus(exc.status_code).description,
        ).response()

    except JsonHTTPException as exc:
        return exc.response()


def setup_middlewares(app: FastAPI):
    app.middleware("http")(catch_exceptions_middleware)

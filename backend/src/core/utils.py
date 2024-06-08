from src.apps.utils.exceptions import JsonHTTPException


def require400(condition, message):
    if not condition:
        raise JsonHTTPException(
            status_code=400,
            error_name="Bad Request",
            error_description=message,
        )

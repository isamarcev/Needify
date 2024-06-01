from src.apps.utils.exceptions import JsonHTTPException


class CurrencyValidationJsonException(JsonHTTPException):
    def __init__(self, description: str):
        super().__init__(
            status_code=400,
            error_name="Validation Error",
            error_description=description,
        )


class CurrencyNotFoundJsonException(JsonHTTPException):
    def __init__(self, symbol: str, description: str = None):
        if not description:
            description = f"Currency {symbol} not found"
        super().__init__(
            status_code=404,
            error_name="Not Found",
            error_description=description,
        )


class CurrencyAddressNotFoundJsonException(JsonHTTPException):
    def __init__(self, address: str, description: str = None):
        if not description:
            description = f"Currency with {address} not found"
        super().__init__(
            status_code=404,
            error_name="Not Found",
            error_description=description,
        )
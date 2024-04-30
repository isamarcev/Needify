from src.apps.utils.exceptions import JsonHTTPException


class DepositWalletValidationJsonException(JsonHTTPException):

    def __init__(self, description: str):
        super().__init__(
            status_code=400,
            error_name="Validation Error",
            error_description=description,
        )


class DepositWalletNotFoundException(JsonHTTPException):
    def __init__(self, address: str):
        super().__init__(
            error_description=f"Deposit wallet not found: {address}",
            status_code=404,
            error_name="Not Found"
        )
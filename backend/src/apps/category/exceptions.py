from src.apps.utils.exceptions import JsonHTTPException


class CategoryNotFoundException(JsonHTTPException):

    def __init__(self):
        super().__init__(
            status_code=404,
            error_name="Not Found",
            error_description="Category not found",
        )

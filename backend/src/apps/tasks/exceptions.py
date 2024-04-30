from src.apps.utils.exceptions import JsonHTTPException


class TaskValidationJsonException(JsonHTTPException):

    def __init__(self, description: str):
        super().__init__(
            status_code=400,
            error_name="Validation Error",
            error_description=description,
        )


class TaskNotFoundJsonException(JsonHTTPException):

    def __init__(self, task_id: int):
        super().__init__(
            status_code=404,
            error_name="Not Found",
            error_description=f"Task #{task_id} not found",
        )

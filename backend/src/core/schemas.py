from pydantic import BaseModel


class ErrorSchema(BaseModel):
    name: str
    code: int
    description: str
    meta: dict


class BaseErrorResponse(BaseModel):
    error: ErrorSchema

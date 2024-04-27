from datetime import datetime
from pydantic_core import core_schema as cs
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
from pydantic.json_schema import JsonSchemaValue


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserSchema(BaseModel):
    id: str = Field(str, alias="_id")
    telegram_id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    image: str | None
    permissions: list[str] | None
    disabled: bool | None
    created: datetime
    updated: datetime | None

    @validator("id", pre=True, always=True)
    def validate_id(cls, v):
        return str(v)

    class Config:
        title = "users"
        populate_by_name = True
        arbitrary_types_allowed = True

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}"


class CreateUserSchema(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    image: str | None = None
    permissions: list[str] | None = None
    disabled: bool = False


class UpdateUserSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    image: str | None = None


class TokenData(BaseModel):
    username: str | None = None

from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, validator


class UserSchema(BaseModel):
    id: str = Field(alias="_id")
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

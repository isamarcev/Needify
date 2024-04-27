from abc import ABC
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError

from src.apps.users.database import BaseUserDatabase
from src.apps.users.schemas import CreateUserSchema, UserSchema, UpdateUserSchema
from src.apps.utils.exceptions import JsonHTTPException


class BaseUserManager(ABC):

    async def create_user(self, *args, **kwargs):
        raise NotImplementedError()

    async def get_user(self, *args, **kwargs):
        raise NotImplementedError()

    async def get_user_by_telegram_id(self, *args, **kwargs):
        raise NotImplementedError()

    async def get_user_by_username(self, *args, **kwargs):
        raise NotImplementedError()

    async def update_user(self, *args, **kwargs):
        raise NotImplementedError()

    async def delete_user(self, *args, **kwargs):
        raise NotImplementedError()


class UserManager(BaseUserManager):

    def __init__(self, user_db: BaseUserDatabase):
        self.user_db = user_db

    async def get_users(self) -> list[UserSchema]:
        users = await self.user_db.get_users()
        return [UserSchema(**user) for user in users]

    async def create_user(self, create_schema: CreateUserSchema):
        dict_to_insert = create_schema.dict()
        dict_to_insert.update({"created": datetime.now(), "updated": datetime.now()})
        try:
            result = await self.user_db.insert_user(**dict_to_insert)
        except DuplicateKeyError as e:
            raise JsonHTTPException(status_code=400,
                                    error_description="User with this telegram_id already exists",
                                    error_name="DUPLICATE_KEY") from e
        return CreateUserSchema(**result)

    async def get_user(self, user_id: str, raise_if_none: bool = True) -> UserSchema | None:
        user = await self.user_db.get_user(user_id)
        if not user and raise_if_none:
            raise JsonHTTPException(status_code=404,
                                    error_description="User not found",
                                    error_name="NOT_FOUND")
        return UserSchema(**user) if user else None

    async def get_user_by_telegram_id(self, telegram_id: int, raise_if_none: bool = True) -> UserSchema | None:
        user = await self.user_db.get_user_by_telegram_id(telegram_id)
        if not user and raise_if_none:
            raise JsonHTTPException(status_code=404,
                                    error_description="User not found",
                                    error_name="NOT_FOUND")
        return UserSchema(**user) if user else None

    async def get_user_by_username(self, username: str, raise_if_none: bool = True) -> UserSchema | None:
        user = await self.user_db.get_user_by_username(username)
        if not user and raise_if_none:
            raise JsonHTTPException(status_code=404,
                                    error_description="User not found",
                                    error_name="NOT_FOUND")
        return UserSchema(**user) if user else None

    async def update_user(self, telegram_id: int, update_schema: UpdateUserSchema, raise_if_none: bool = True) -> UserSchema | None:
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user and raise_if_none:
            raise JsonHTTPException(status_code=404,
                                    error_description="User not found",
                                    error_name="NOT_FOUND")
        dict_to_update = update_schema.dict(exclude_unset=True)
        dict_to_update.update({"updated": datetime.now()})
        result = await self.user_db.update_user(user.telegram_id, dict_to_update)
        return UserSchema(**result) if result else None

    async def delete_user(self, telegram_id: int, raise_if_none: bool = True) -> None:
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user and raise_if_none:
            raise JsonHTTPException(status_code=404,
                                    error_description="User not found",
                                    error_name="NOT_FOUND")
        await self.user_db.delete_user(telegram_id)

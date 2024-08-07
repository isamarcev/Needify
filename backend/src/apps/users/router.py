import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette import status

from src.apps.users.manager import UserManager
from src.apps.users.schemas import (
    CreateUserSchema,
    UpdateUserSchema,
    UserSchema,
    UserWeb3WalletSchema,
)
from src.apps.utils.exceptions import JsonHTTPException

telegram_logger = logging.getLogger("telegram_logger")

user_router = APIRouter()


@user_router.get("/list")
@inject
async def get_users(
    user_manager: UserManager = Depends(Provide["user_container.user_manager"]),
) -> list[UserSchema]:
    users = await user_manager.get_users()
    return users


@user_router.get("/{telegram_id}")
@inject
async def get_user(
    telegram_id: int,
    user_manager: UserManager = Depends(Provide["user_container.user_manager"]),
) -> UserSchema:
    user = await user_manager.get_user_by_telegram_id(telegram_id)
    telegram_logger.info(
        f"Getting user with telegram_id: {telegram_id}. \n " f"User data: {user.username=}"
    )
    if user is None:
        raise JsonHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_name="NOT_FOUND",
            error_description=f"User with telegram_id {telegram_id} not found",
        )
    return user


@user_router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    user_schema: CreateUserSchema,
    user_manager: UserManager = Depends(Provide["user_container.user_manager"]),
):
    telegram_logger.info(f"Creating user with data: {user_schema.dict()}")
    created_user = await user_manager.create_user(user_schema)
    return created_user


@user_router.put("/{telegram_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
@inject
async def update_user(
    telegram_id: int,
    user_schema: UpdateUserSchema,
    user_manager: UserManager = Depends(Provide["user_container.user_manager"]),
):
    telegram_logger.info(f"Updating user with telegram_id: {telegram_id}. ")
    updated_user = await user_manager.update_user(telegram_id, user_schema)
    return updated_user


@user_router.delete("/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    telegram_id: int,
    user_manager: UserManager = Depends(Provide["user_container.user_manager"]),
):
    await user_manager.delete_user(telegram_id)
    return {"message": "User deleted successfully"}


@user_router.post("/wallet/add", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
@inject
async def add_wallet_user(
    wallet_data: UserWeb3WalletSchema,
    telegram_id: int,
    user_manager: UserManager = Depends(Provide["user_container.user_manager"]),
):
    telegram_logger.info(
        f"Adding wallet for user with telegram_id: {telegram_id}. "
        f"Wallet address: {wallet_data.address}"
    )
    user = await user_manager.add_wallet(telegram_id, wallet_data)
    return user

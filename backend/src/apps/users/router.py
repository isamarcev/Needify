from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.apps.users.dependencies import UserContainer
from src.apps.users.manager import UserManager
from src.apps.users.schemas import CreateUserSchema, UserSchema, UpdateUserSchema
from src.apps.utils.exceptions import JsonHTTPException
from src.core.security import authenticate_user, create_access_token

user_router = APIRouter()


# @user_router.post("/token",)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
#     user = await authenticate_user(form_data.username)
#     if not user:
#         raise JsonHTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             error_name="UNAUTHORIZED",
#             error_description="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = await create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/list")
@inject
async def get_users(user_manager: UserManager = Depends(Provide[UserContainer.user_manager])) -> list[UserSchema]:
    users = await user_manager.get_users()
    return users


@user_router.get("/{telegram_id}")
@inject
async def get_user(telegram_id: int, user_manager: UserManager = Depends(Provide[UserContainer.user_manager])) -> UserSchema:
    user = await user_manager.get_user_by_telegram_id(telegram_id)
    if user is None:
        raise JsonHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_name="NOT_FOUND",
            error_description=f"User with telegram_id {telegram_id} not found",
        )
    return user


@user_router.post("/")
@inject
async def create_user(user_schema: CreateUserSchema, user_manager: UserManager = Depends(Provide[UserContainer.user_manager])):
    created_user = await user_manager.create_user(user_schema)
    return created_user


@user_router.put("/{telegram_id}")
@inject
async def update_user(telegram_id: int, user_schema: UpdateUserSchema,
                      user_manager: UserManager = Depends(Provide[UserContainer.user_manager])):
    updated_user = await user_manager.update_user(telegram_id, user_schema)
    return updated_user


@user_router.delete("/{telegram_id}")
@inject
async def delete_user(telegram_id: int, user_manager: UserManager = Depends(Provide[UserContainer.user_manager])):
    await user_manager.delete_user(telegram_id)
    return {"message": "User deleted successfully"}
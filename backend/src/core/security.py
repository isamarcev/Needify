from http import HTTPStatus

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

# from src.apps.users.dependencies import user_manager
# from src.apps.users.schemas import TokenData
from src.apps.utils.exceptions import JsonHTTPException
from src.core.config import security_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# async def authenticate_user(username: str):
#     user = await user_manager.get_user_by_username(username)
#     if not user:
#         return False
#     return user


async def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(
        to_encode,
        security_settings.TOKEN_SECRET_KEY,
        algorithm=security_settings.TOKEN_ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = JsonHTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        error_name="UNAUTHORIZED",
        error_description="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            security_settings.token_secret_key,
            algorithms=[security_settings.algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
    except jwt.exceptions.InvalidTokenError:
        raise credentials_exception
    # user = await user_manager.get_user_by_username(username=token_data.username)
    user = None
    if user is None:
        raise credentials_exception
    return user

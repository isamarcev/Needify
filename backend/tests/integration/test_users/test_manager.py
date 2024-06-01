import pytest

from src.apps.users.schemas import CreateUserSchema
from src.apps.utils.exceptions import JsonHTTPException


@pytest.mark.asyncio
async def test_create_user(user_container):
    user = {
        "telegram_id": 1,
        "username": "@test_user",
        "first_name": "Test",
        "last_name": "User",
    }

    second_user = {
        "telegram_id": 2,
        "username": "@test_user2",
        "first_name": "Test2",
        "last_name": "User2",
    }
    user_manager = user_container.user_manager()
    users = await user_manager.get_users()
    schema = CreateUserSchema(**user)
    created_user = await user_manager.create_user(schema)
    users_after = await user_manager.get_users()
    assert created_user.telegram_id == user["telegram_id"]
    with pytest.raises(JsonHTTPException) as exc_info:
        await user_manager.create_user(schema)

    # Assert that the correct error name and description are provided
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_name == "DUPLICATE_KEY"
    assert exc_info.value.error_description == "User with this telegram_id already exists"
    users_after_error = await user_manager.get_users()

    assert len(users) + 1 == len(users_after)
    assert len(users_after) == len(users_after_error)

    schema = CreateUserSchema(**second_user)
    created_user = await user_manager.create_user(schema)
    users_after = await user_manager.get_users()
    assert created_user.telegram_id == second_user["telegram_id"]
    assert len(users) + 2 == len(users_after)

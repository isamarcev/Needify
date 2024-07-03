import pytest

from src.apps.tasks.enums import TaskStatusEnum
from src.apps.tasks.schemas import PreCreateTaskSchema
from tests.integration.datasets.task import task_data


@pytest.mark.asyncio
async def test_create_task(mocker, core_container):
    task_manager = await core_container.task_container.task_manager()
    mocker.patch(
        "src.apps.tasks.manager.TaskManager.check_poster_balance_for_deploy", return_value=None
    )
    created_task = await task_manager.create_task(PreCreateTaskSchema(**task_data))
    assert created_task.title == task_data["title"]
    assert created_task.description == task_data["description"]
    assert created_task.category == task_data["category"]
    assert created_task.images == task_data["images"]
    assert created_task.price == task_data["price"]
    assert created_task.currency == task_data["currency"]
    assert created_task.poster_id == task_data["poster_id"]
    assert created_task.status == TaskStatusEnum.PRE_CREATED

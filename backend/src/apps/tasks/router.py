from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette import status

from src.apps.tasks.dependencies import TaskContainer
from src.apps.tasks.manager import TaskManager
from src.apps.tasks.schemas import (
    PreCreateTaskSchema,
    TaskSchema,
    UpdateStatusTaskSchema,
    UserHistoryResponseSchema,
)
from src.core.schemas import BaseErrorResponse

task_router = APIRouter()


@task_router.get(
    "/",
    response_model=list[TaskSchema],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": TaskSchema},
    },
)
@inject
async def get_list_tasks(
    category: str | None = None,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    tasks = await task_manager.get_tasks(category=category)
    return tasks


@task_router.get(
    "/{task_id}",
    response_model=TaskSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": TaskSchema},
    },
)
@inject
async def get_task(
    task_id: int,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    task = await task_manager.get_by_task_id(task_id)
    return task


@task_router.post(
    "/",
    response_model=TaskSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": TaskSchema},
    },
)
@inject
async def create_task(
    data_to_create: PreCreateTaskSchema,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.create_task(data_to_create)


@task_router.put(
    "/{task_id}",
    response_model=TaskSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": TaskSchema},
    },
)
@inject
async def update_task_status(
    task_id: int,
    data_to_update: UpdateStatusTaskSchema,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.update_task_status(task_id, data_to_update)


@task_router.get(
    "/{user_id}/tasks",
    response_model=UserHistoryResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": UserHistoryResponseSchema},
    },
)
@inject
async def get_tasks_by_user_id(
    user_id: int,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.get_user_tasks(user_id)

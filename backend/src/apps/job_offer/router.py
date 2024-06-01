from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette import status

from src.apps.tasks.dependencies import TaskContainer
from src.apps.tasks.manager import TaskManager
from src.apps.tasks.schemas import (
    ChooseDoerSchema,
    CompleteJob,
    ConfirmJob,
    GetJob,
    JobOfferMessageDeployResponseSchema,
    JobOfferMessageResponseSchema,
    JobOfferMessageSchema,
    RevokeJob,
)
from src.core.schemas import BaseErrorResponse

job_offer_router = APIRouter()


@job_offer_router.post(
    "/message/deploy",
    response_model=JobOfferMessageDeployResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": JobOfferMessageDeployResponseSchema},
    },
)
@inject
async def get_deploy_job_offer_message(
    data: JobOfferMessageSchema,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.get_user_tasks(data)


@job_offer_router.post(
    "/message/get-job",
    response_model=JobOfferMessageResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": JobOfferMessageResponseSchema},
    },
)
@inject
async def get_job_offer_message(
    data: GetJob,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.get_user_tasks(data)


@job_offer_router.post(
    "/message/choose-doer",
    response_model=JobOfferMessageResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": JobOfferMessageResponseSchema},
    },
)
@inject
async def choose_doer_job_offer_message(
    data: ChooseDoerSchema,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.get_user_tasks(data)


@job_offer_router.post(
    "/message/complete",
    response_model=JobOfferMessageResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": JobOfferMessageResponseSchema},
    },
)
@inject
async def complete_job_offer_message(
    data: CompleteJob,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.get_user_tasks(data)


@job_offer_router.post(
    "/message/confirm",
    response_model=JobOfferMessageResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": JobOfferMessageResponseSchema},
    },
)
@inject
async def confirm_job_offer_message(
    data: ConfirmJob,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.get_user_tasks(data)


@job_offer_router.post(
    "/message/revoke",
    response_model=JobOfferMessageResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": JobOfferMessageResponseSchema},
    },
)
@inject
async def revoke_job_offer_message(
    data: RevokeJob,
    task_manager: TaskManager = Depends(Provide[TaskContainer.task_manager]),
):
    return await task_manager.get_user_tasks(data)

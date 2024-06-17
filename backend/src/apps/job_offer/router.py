
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette import status

from src.apps.job_offer.manager import JobOfferManager
from src.apps.job_offer.schemas import (
    ChooseDoerSchema,
    CompleteJob,
    ConfirmJob,
    GetJob,
    JobOfferMessageResponseSchema,
    JobOfferMessageSchema,
    RevokeJob,
    TONConnectMessageResponse,
)
from src.core.schemas import BaseErrorResponse

job_offer_router = APIRouter()


@job_offer_router.post(
    "/message/deploy",
    response_model=TONConnectMessageResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": TONConnectMessageResponse},
    },
)
@inject
async def get_deploy_job_offer_message(
    data: JobOfferMessageSchema,
    job_offer_manager: JobOfferManager = Depends(Provide["job_offer_container.job_offer_manager"]),
):
    return await job_offer_manager.create_deploy_message(data)


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
    job_offer_manager: JobOfferManager = Depends(Provide["job_offer_container.job_offer_manager"]),
):
    return await job_offer_manager.create_get_job_message(data)


@job_offer_router.post(
    "/message/choose-doer",
    response_model=TONConnectMessageResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
        status.HTTP_200_OK: {"model": JobOfferMessageResponseSchema},
    },
)
@inject
async def choose_doer_job_offer_message(
    data: ChooseDoerSchema,
    job_offer_manager: JobOfferManager = Depends(Provide["job_offer_container.job_offer_manager"]),
):
    return await job_offer_manager.create_choose_doer_message(data)


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
    job_offer_manager: JobOfferManager = Depends(Provide["job_offer_container.job_offer_manager"]),
):
    return await job_offer_manager.create_complete_message(data)


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
    job_offer_manager: JobOfferManager = Depends(Provide["job_offer_container.job_offer_manager"]),
):
    return await job_offer_manager.create_confirm_message(data)


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
    job_offer_manager: JobOfferManager = Depends(Provide["job_offer_container.job_offer_manager"]),
):
    return await job_offer_manager.create_revoke_message(data)


# @job_offer_router.post(
#     "/message/get-job-offer-chain-state",
#     # response_model=JobOfferMessageResponseSchema,
#     responses={
#         status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
#         status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
#         # status.HTTP_200_OK: {"model": JobOfferMessageResponseSchema},
#     },
# )
# @inject
# async def get_job_offer_chain_state(
#     data: JobOfferMessageSchema,
#     job_offer_manager: JobOfferManager = Depends(Provide[JobOfferContainer.job_offer_manager]),
# ) -> Any:
#     return await job_offer_manager.get_job_offer_chain_state(task_id=data.task_id)
#
#
# @job_offer_router.get(
#     "/vacancies",
#     # response_model=JobOfferMessageResponseSchema,
#     responses={
#         status.HTTP_400_BAD_REQUEST: {"model": BaseErrorResponse},
#         status.HTTP_404_NOT_FOUND: {"model": BaseErrorResponse},
#         # status.HTTP_200_OK: {"model": JobOfferMessageResponseSchema},
#     },
# )
# @inject
# async def test_job_offer_vacancies(
#     address: str,
#     job_offer_manager: JobOfferManager =
#     Depends(Provide["job_offer_container.job_offer_manager"]),
# ):
#     return await job_offer_manager.get_job_vacancies(job_offer_address=address)

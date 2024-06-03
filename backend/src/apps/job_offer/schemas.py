from typing import List

from pydantic import BaseModel, PositiveInt

from src.apps.tasks.schemas import TONConnectMessageSchema


class JobOfferMessageSchema(BaseModel):
    task_id: PositiveInt
    action_by_user: PositiveInt


class ChooseDoerSchema(JobOfferMessageSchema):
    doer: str


class CompleteJob(JobOfferMessageSchema):
    pass


class GetJob(JobOfferMessageSchema):
    pass


class ConfirmJob(JobOfferMessageSchema):
    mark: PositiveInt | None = None
    review: str | None = None


class RevokeJob(JobOfferMessageSchema):
    pass


class AppealJob(JobOfferMessageSchema):
    pass


class JobOfferMessageResponseSchema(BaseModel):
    valid_until: int
    messages: List[TONConnectMessageSchema]


class JobOfferMessageDeployResponseSchema(BaseModel):
    valid_until: int
    messages: List[TONConnectMessageSchema]

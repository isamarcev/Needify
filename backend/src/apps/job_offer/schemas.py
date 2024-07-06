from typing import List, TypedDict

from pydantic import BaseModel, PositiveInt
from typing_extensions import NotRequired

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
    validUntil: int
    messages: List[TONConnectMessageSchema]


class TONConnectMessageResponse(BaseModel):
    validUntil: int
    messages: List[TONConnectMessageSchema]


class MessageDTO(TypedDict):
    address: str
    amount: str
    payload: str
    stateInit: NotRequired[str]


class JobOfferDataDTO(TypedDict):
    title: str
    description: str
    price: int
    owner: str
    doer: NotRequired[str]
    state: int
    balance: int
    jetton_wallet: str
    native_wallet: str
    jetton_balance: int
    native_balance: int
    appeal_address: NotRequired[str]
    mark: NotRequired[int]
    review: NotRequired[str]

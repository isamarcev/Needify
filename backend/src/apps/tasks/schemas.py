from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, PositiveFloat, PositiveInt

from src.apps.tasks.enums import TaskStatusEnum


class TaskTitle(str):
    MAX_LENGTH = 255

    def __new__(cls, value):
        if len(value) > cls.MAX_LENGTH:
            raise ValueError(f"Title length cannot exceed {cls.MAX_LENGTH} characters")
        return str.__new__(cls, value)


class TaskDescription(str):
    MAX_LENGTH = 1000

    def __new__(cls, value):
        if len(value) > cls.MAX_LENGTH:
            raise ValueError(f"Title length cannot exceed {cls.MAX_LENGTH} characters")
        return str.__new__(cls, value)


class VacancySchema(BaseModel):
    doer: str
    telegram_id: int


class JobOfferSchema(BaseModel):
    job_offer_address: str
    jetton_master_address: str
    jetton_native_address: str
    state: str
    stateInit: str
    owner: str
    doer: str | None = None
    vacancies: List[VacancySchema]
    mark: int | None = None
    review: str | None = None


class TaskSchema(BaseModel):
    task_id: int
    title: TaskTitle
    description: TaskDescription
    images: list[str] = []
    category: str
    price: PositiveFloat
    currency: str

    status: TaskStatusEnum = TaskStatusEnum.PRE_CREATED
    poster_id: PositiveInt
    poster_address: str

    doer_id: int | None = None
    doer_address: str | None = None

    job_offer: JobOfferSchema | None = None

    deadline: datetime
    created_at: datetime
    updated_at: datetime | None = None


class PreCreateTaskSchema(BaseModel):
    title: TaskTitle
    description: TaskDescription
    category: str
    images: List[str] = Field(..., description="Image in string format")
    price: PositiveFloat
    currency: str = Field(..., description="Currency symbol")

    poster_id: PositiveInt = Field(..., description="Customer telegram ID")
    poster_address: str = Field(..., description="Customer wallet jetton_master_address")
    deadline: datetime


class CreateTaskSchema(PreCreateTaskSchema):
    task_id: int
    status: TaskStatusEnum = TaskStatusEnum.PRE_CREATED
    native_currency: str
    created_at: datetime = Field(default_factory=datetime.now)


class UserHistoryResponseSchema(BaseModel):
    published_tasks: list[TaskSchema]
    picked_up_tasks: list[TaskSchema]
    completed_tasks: list[TaskSchema]


class UpdateStatusTaskSchema(BaseModel):
    status: TaskStatusEnum
    action_by_user_id: int


class JobOfferMessageSchema(BaseModel):
    task_id: int
    action_by_user: int


class ChooseDoerSchema(JobOfferMessageSchema):
    doer: str


class CompleteJob(JobOfferMessageSchema):
    pass


class GetJob(JobOfferMessageSchema):
    pass


class ConfirmJob(JobOfferMessageSchema):
    mark: int | None = None
    review: str | None = None


class RevokeJob(JobOfferMessageSchema):
    pass


class AppealJob(JobOfferMessageSchema):
    pass


class TONConnectMessageSchema(BaseModel):
    address: str = Field(..., description="TON/JettonWallet/etc jetton_master_address")
    amount: str = Field(..., description="String amount in nanoTON")
    payload: str = Field(..., description="Base64 encoded string")


class JobOfferMessageResponseSchema(BaseModel):
    valid_until: int
    messages: List[TONConnectMessageSchema]


class JobOfferMessageDeployResponseSchema(BaseModel):
    valid_until: int
    messages: List[TONConnectMessageSchema]
    stateInit: str

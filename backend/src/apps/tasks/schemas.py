import random
from datetime import datetime

from pydantic import BaseModel, PositiveInt, PositiveFloat, Field

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


class TaskSchema(BaseModel):
    task_id: int
    title: TaskTitle
    description: TaskDescription
    category: str
    status: TaskStatusEnum = TaskStatusEnum.PRE_CREATED
    images: list[str] = []
    task_deposit_address: str
    price: PositiveFloat
    currency: str

    customer_id: PositiveInt
    customer_wallet_address: str

    doer_id: int | None = None
    doer_wallet_address: str | None = None

    deadline: datetime
    created_at: datetime
    updated_at: datetime | None = None


class PreCreateTaskSchema(BaseModel):
    title: TaskTitle
    description: TaskDescription
    category: str
    images: list[str] = []
    price: PositiveFloat
    currency: str

    customer_id: PositiveInt = Field(..., description="Customer telegram ID")
    customer_wallet_address: str = Field(..., description="Customer wallet address")
    deadline: datetime


class CreateTaskSchema(PreCreateTaskSchema):
    task_id: int
    status: TaskStatusEnum = TaskStatusEnum.PRE_CREATED
    task_deposit_address: str = Field(..., description="Deposit address")
    created_at: datetime = Field(default_factory=datetime.now)


class UserHistoryResponseSchema(BaseModel):
    published_tasks: list[TaskSchema]
    picked_up_tasks: list[TaskSchema]
    completed_tasks: list[TaskSchema]


class UpdateStatusTaskSchema(BaseModel):
    status: TaskStatusEnum
    action_by_user_id: int



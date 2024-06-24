from datetime import datetime
from typing import List, Optional

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
    is_chosen: bool = False


class JobOfferSchema(BaseModel):
    job_offer_address: str
    jetton_master_address: str
    jetton_native_address: str
    state: str | None = None
    owner: str
    doer: str | None = None
    vacancies: List[VacancySchema] = []
    mark: int | None = None
    review: str | None = None


class TaskSchema(BaseModel):
    task_id: int
    title: TaskTitle
    description: TaskDescription
    images: Optional[List[str]] = Field(..., description="Image in string format")
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

    class Config:
        schema_extra = {
            "response_example": {
                "task_id": 1,
                "title": "Some title",
                "description": "Some description",
                "images": ["https://someimage.com"],
                "category": "Some category",
                "price": 100.0,
                "currency": "USD",
                "status": "PRE_CREATED",
                "poster_id": 1,
                "poster_address": "0QBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8ItwboL_",
                "doer_id": 2,
                "doer_address": "0QBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8ItwboL_",
                "job_offer": {
                    "job_offer_address": "0QBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8ItwboL_",
                    "jetton_master_address": "0QBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8ItwboL_",
                    "jetton_native_address": "0QBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8ItwboL_",
                    "state": "Some state",
                    "owner": "Some owner",
                    "doer": "Some doer",
                    "vacancies": [{"doer": "Some doer", "telegram_id": 1, "is_chosen": False}],
                    "mark": 1,
                    "review": "Some review",
                },
                "deadline": "2021-09-01T00:00:00",
                "created_at": "2021-09-01T00:00:00",
                "updated_at": "2021-09-01T00:00:00",
            }
        }


class PreCreateTaskSchema(BaseModel):
    title: TaskTitle
    description: TaskDescription
    category: str
    images: Optional[List[str]] = None
    price: PositiveFloat
    currency: str = Field(..., description="Currency symbol")
    poster_id: PositiveInt = Field(..., description="Customer telegram ID")
    deadline: datetime


class CreateTaskSchema(PreCreateTaskSchema):
    task_id: int
    status: TaskStatusEnum = TaskStatusEnum.PRE_CREATED
    native_currency: str
    created_at: datetime = Field(default_factory=datetime.now)
    poster_address: str


class UserHistoryResponseSchema(BaseModel):
    published_tasks: list[TaskSchema]
    picked_up_tasks: list[TaskSchema]
    completed_tasks: list[TaskSchema]


class UpdateStatusTaskSchema(BaseModel):
    status: TaskStatusEnum
    action_by_user_id: int


class TONConnectMessageSchema(BaseModel):
    address: str = Field(..., description="TON/JettonWallet/etc address")
    amount: str = Field(..., description="String amount in nanoTON")
    payload: str = Field(..., description="Base64 encoded string")
    stateInit: str | None = None

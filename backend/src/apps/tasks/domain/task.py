from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    task_id: int
    title: str
    description: str
    images: list[str]
    category: str
    price: int
    currency: str
    deadline: datetime
    status: str

    poster_id: int
    poster_address: str

    created_at: datetime | None = datetime.now()
    updated_at: datetime | None = None
    doer_id: int | None = None
    doer_address: str | None = None

    def create_deploy_message(self):
        pass

    def representation(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "images": self.images,
            "category": self.category,
            "price": self.price,
            "currency": self.currency,
            "deadline": self.deadline,
            "status": self.status,
            "poster_id": self.poster_id,
            "poster_address": self.poster_address,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "doer_id": self.doer_id,
            "doer_address": self.doer_address,
        }

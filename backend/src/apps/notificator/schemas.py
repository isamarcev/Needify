from pydantic import BaseModel, PositiveInt


class SendNotificationSchema(BaseModel):
    user_telegram_id: PositiveInt
    task_id: PositiveInt
    task_title: str
    new_task_status: str

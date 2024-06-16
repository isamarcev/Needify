from pydantic import BaseModel, PositiveInt


class SendNotificationSchema(BaseModel):
    user_telegram_id: PositiveInt
    text: str

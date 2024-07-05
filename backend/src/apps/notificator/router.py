from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.notificator.dependencies import NotificatorContainer
from src.apps.notificator.manager import NotificatorManager
from src.apps.notificator.schemas import SendNotificationSchema

notificator_router = APIRouter()


@notificator_router.post("/send")
@inject
async def get_deploy_job_offer_message(
    data: SendNotificationSchema,
    notificator_manager: NotificatorManager = Depends(
        Provide[NotificatorContainer.notificator_manager]
    ),
):
    await notificator_manager.send_notification(
        data.user_telegram_id, data.task_id, data.task_title, data.new_task_status
    )
    return {"status": "ok"}

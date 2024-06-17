from fastapi import APIRouter

from src.apps.category.routes import category_router
from src.apps.currency.router import currency_router
from src.apps.job_offer.router import job_offer_router
from src.apps.notificator.router import notificator_router
from src.apps.scanner.router import scanner_router
from src.apps.tasks.router import task_router
from src.apps.TONconnect.router import ton_connect
from src.apps.users.router import user_router

# from src.apps.wallets.router import jetton_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(user_router, prefix="/users", tags=["users"])
v1_router.include_router(currency_router, prefix="/currency", tags=["currency"])
# v1_router.include_router(jetton_router, prefix="/jetton", tags=["jetton"])
v1_router.include_router(scanner_router, prefix="/scanner", tags=["scanner"])
v1_router.include_router(task_router, prefix="/task", tags=["task"])
v1_router.include_router(job_offer_router, prefix="/job-offer", tags=["job-offer"])
v1_router.include_router(category_router, prefix="/category", tags=["category"])
v1_router.include_router(ton_connect, prefix="/ton-connect", tags=["ton-connect"])
v1_router.include_router(notificator_router, prefix="/notificator", tags=["notificator"])

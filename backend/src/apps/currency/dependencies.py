from src.apps.currency.manager import CurrencyManager
from src.core.database import async_mongo
from src.core.provider import get_lite_server_client
from src.core.repository import BaseMongoRepository


async def get_currency_repository():
    return BaseMongoRepository(
        async_mongo,
        collection_name="currency"
    )


async def get_currency_manager() -> CurrencyManager:
    ltx = await get_lite_server_client()
    return CurrencyManager(
        lts_client=ltx,
        repository=await get_currency_repository()
    )
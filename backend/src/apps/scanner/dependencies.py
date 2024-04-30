from src.apps.scanner.manager import ScannerManager
from src.core.cache import RedisCacheDatabase
from src.core.database import redis_database
from src.core.provider import get_tonsdk_center_client, get_lite_server_client


async def get_scanner_manager() -> ScannerManager:
    ton_center_provider = await get_tonsdk_center_client()
    lts_provider = await get_lite_server_client()
    redis = RedisCacheDatabase(
        redis=redis_database
    )
    return ScannerManager(
        lt_server_provider=lts_provider,
        toncenter_provider=ton_center_provider,
        cache_database=redis
    )
from fastapi import APIRouter, Depends

from src.apps.scanner.dependencies import get_scanner_manager
from src.apps.scanner.manager import ScannerManager

scanner_router = APIRouter()


@scanner_router.get("/get_last_masterchain_block")
async def get_last_masterchain_block(
    scanner_manager: ScannerManager = Depends(get_scanner_manager),
):
    last_masterchain_block = await scanner_manager.scan_last_block_masterchain()
    return {"scan_last_block_masterchain": last_masterchain_block}

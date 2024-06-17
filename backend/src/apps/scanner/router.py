from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.scanner.service import BlockScanner

# from src.apps.scanner.dependencies import get_scanner_manager
# from src.apps.scanner.manager import ScannerManager

scanner_router = APIRouter()


@scanner_router.get("/manual_scan")
@inject
async def get_last_masterchain_block(
    block_: int,
    scanner_manager: BlockScanner = Depends(Provide["scanner_service"]),
):
    last_masterchain_block = await scanner_manager.manual_scan(block_)
    return {"scan_last_block_masterchain": last_masterchain_block}

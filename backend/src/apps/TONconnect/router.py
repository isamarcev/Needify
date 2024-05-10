from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.apps.TONconnect.dependencies import TONConnectContainer
from src.apps.TONconnect.manager import TONConnectManager
from src.apps.TONconnect.schemas import ConnectDepositSchema

# from src.apps.scanner.dependencies import get_scanner_manager
# from src.apps.scanner.manager import ScannerManager

ton_connect = APIRouter()


@ton_connect.post("/test")
@inject
async def get_last_masterchain_block(
    data: ConnectDepositSchema,
    scanner_manager: TONConnectManager = Depends(
        Provide[TONConnectContainer.ton_connect_manager]
    ),
):
    last_masterchain_block = await scanner_manager.test(data)
    return {"scan_last_block_masterchain": last_masterchain_block}

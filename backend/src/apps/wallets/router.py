from fastapi import APIRouter, Depends

from src.apps.wallets.jetton_manager import JettonManager
from src.apps.wallets.dependencies import get_jetton_manager, get_main_wallet
from src.apps.wallets.schemas import JettonTransferSchema
from src.core.config import config

jetton_router = APIRouter()


@jetton_router.post("/transfer")
async def transfer_jetton(transfer_data: JettonTransferSchema, jetton_manager: JettonManager = Depends(get_jetton_manager)):
    main_wallet = await get_main_wallet()
    return await jetton_manager.transfer(
        wallet=main_wallet,
        destination_address=transfer_data.destination_address,
        amount=transfer_data.amount,
        jetton_master_address=config.NATIVE_JETTON_ADDRESS
    )

from base64 import urlsafe_b64encode
from datetime import time

from pytoniq_core import begin_cell


def get_jetton_transfer_message(
    jetton_wallet_address: str,
    recipient_address: str,
    transfer_fee: int,
    jettons_amount: int,
    response_address: str = None,
) -> dict:
    data = {
        "address": jetton_wallet_address,
        "amount": str(transfer_fee),
        "payload": urlsafe_b64encode(
            begin_cell()
            .store_uint(0xF8A7EA5, 32)  # op code for jetton transfer message
            .store_uint(0, 64)  # query_id
            .store_coins(jettons_amount)
            .store_address(recipient_address)  # destination address
            .store_address(
                response_address or recipient_address
            )  # address send excess to
            .store_uint(0, 1)  # custom payload
            .store_coins(1)  # forward amount
            .store_uint(0, 1)  # forward payload
            .end_cell()  # end cell
            .to_boc()  # convert it to boc
        ).decode(),  # encode it to urlsafe base64
    }

    return data


def get_ton_transfer_message(
    jetton_wallet_address: str,
    recipient_address: str,
    transfer_fee: int,
    jettons_amount: int,
    response_address: str = None,
) -> dict:
    data = {
        "address": jetton_wallet_address,
        "amount": str(transfer_fee),
        "payload": urlsafe_b64encode(
            begin_cell()
            .store_uint(0xF8A7EA5, 32)  # op code for jetton transfer message
            .store_uint(0, 64)  # query_id
            .store_coins(jettons_amount)
            .store_address(recipient_address)  # destination address
            .store_address(
                response_address or recipient_address
            )  # address send excess to
            .store_uint(0, 1)  # custom payload
            .store_coins(1)  # forward amount
            .store_uint(0, 1)  # forward payload
            .end_cell()  # end cell
            .to_boc()  # convert it to boc
        ).decode(),  # encode it to urlsafe base64
    }

    return data


# transaction = {
#     'valid_until': int(time.time() + 3600),
#     'messages': [
#         get_jetton_transfer_message(
#         jetton_wallet_address='EQCXsVvdxTVmSIvYv4tTQoQ-0Yq9mERGTKfbsIhedbN5vTVV',
#         recipient_address='0:0000000000000000000000000000000000000000000000000000000000000000',
#         transfer_fee=int(0.07 * 10**9),
#         jettons_amount=int(0.01 * 10**9),  # replace 9 for jetton decimal. For example for jUSDT it should be (amount * 10**6)
#         response_address=wallet_address
#         ),
#     ]
# }

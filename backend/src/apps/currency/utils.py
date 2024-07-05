import base64

from pytoniq_core import Cell, begin_cell


def get_jetton_transfer_payload(
    recipient_address: str, jettons_amount: int, forward_amount: int, response_address: str = None
) -> Cell:
    payload = begin_cell()
    payload.store_uint(0xF8A7EA5, 32)  # op code for jetton transfer message
    payload.store_uint(0, 64)  # query_id
    payload.store_coins(jettons_amount)
    payload.store_address(recipient_address)  # destination address
    payload.store_address(response_address or recipient_address)  # address send excess to
    payload.store_uint(0, 1)  # custom payload
    payload.store_coins(forward_amount)  # forward amount
    payload.store_uint(0, 1)  # forward payload
    return payload.end_cell()


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
        "payload": base64.urlsafe_b64encode(
            begin_cell()
            .store_uint(0xF8A7EA5, 32)  # op code for jetton transfer message
            .store_uint(0, 64)  # query_id
            .store_coins(jettons_amount)
            .store_address(recipient_address)  # destination address
            .store_address(response_address or recipient_address)  # address send excess to
            .store_uint(0, 1)  # custom payload
            .store_coins(1)  # forward amount
            .store_uint(0, 1)  # forward payload
            .end_cell()  # end cell
            .to_boc()  # convert it to boc
        ).decode(),  # encode it to urlsafe base64
    }

    return data

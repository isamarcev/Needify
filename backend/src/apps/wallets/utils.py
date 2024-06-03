from base64 import urlsafe_b64encode

from pytoniq_core import begin_cell
from tonsdk.boc import Builder, Cell, Slice
from tonsdk.utils import Address


def read_string_tail(string_slice: Slice):
    if len(string_slice) % 8 != 0:
        raise Exception(f"Invalid string length: {len(string_slice) // 8}")

    if len(string_slice.refs) > 1:
        raise Exception("Too many refs in string tail")

    if len(string_slice.refs) == 1 and 1023 - len(string_slice) > 7:
        raise Exception(f"Invalid string length: {len(string_slice) // 8}")

    text_bytes = b""

    if len(string_slice) != 0:
        text_bytes = string_slice.read_bytes(len(string_slice) // 8)

    if len(string_slice.refs) - string_slice.ref_offset == 1:
        text_bytes += read_string_tail(string_slice.read_ref().begin_parse())

    return text_bytes


def write_string_tail(text: bytes, builder: Builder):
    if len(text) <= 0:
        return

    free_bytes = builder.bits.get_free_bits() // 8

    if len(text) <= free_bytes:
        builder.store_bytes(text)
        return

    available = text[:free_bytes]
    tail = text[free_bytes:]
    builder.store_bytes(available)
    new_builder = Builder()
    write_string_tail(tail, new_builder)
    builder.store_ref(new_builder.end_cell())


def string_to_cell(text: str):
    builder = Builder()
    write_string_tail(bytes(text, encoding="utf8"), builder)
    return builder.end_cell()


def cell_to_string(string_cell: Cell):
    return read_string_tail(string_cell.begin_parse()).decode("utf8")


def string_as_comment(text: str):
    return bytes([0b0, 0b0, 0b0, 0b0] + list(text.encode())).decode()


def get_jetton_transfer_message(
    jetton_wallet_address: str | Address,
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
            .store_address(response_address or recipient_address)  # address send excess to
            .store_uint(0, 1)  # custom payload
            .store_coins(1)  # forward amount
            .store_uint(0, 1)  # forward payload
            .end_cell()  # end cell
            .to_boc()  # convert it to boc
        ).decode(),  # encode it to urlsafe base64
    }

    return data


def get_ton_transfer_message() -> dict:
    raise NotImplementedError()

from typing import TypedDict

from pytoniq_core import Address

from src.apps.transaction.enums import MessageTypeEnum


class RawMessageDTO(TypedDict):
    message_type: MessageTypeEnum
    src: Address | None
    dest: Address
    op_code: int
    created_lt: int
    init: str | None
    body: str


class RawTransactionDTO(TypedDict):
    account_address: Address
    hash: str
    compute_phase_code: int | None
    action_phase_code: int | None
    total_fee: int
    lt: int
    now: int
    bag_of_cell: str
    in_msg: RawMessageDTO
    out_msgs: list[RawMessageDTO]

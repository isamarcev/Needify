import logging

from pytoniq_core import Address, ExternalMsgInfo, InternalMsgInfo, MessageAny, Transaction
from tonsdk.utils import bytes_to_b64str

from src.apps.transaction.enums import MessageTypeEnum
from src.apps.transaction.schemas import RawMessageDTO, RawTransactionDTO


class TransactionService:
    def __init__(self):
        pass

    async def parse_transaction(self, transaction: Transaction) -> RawTransactionDTO:
        computation_exit_code = None
        action_exit_code = None
        hash_ = transaction.cell.get_hash(0).hex()
        account_address = Address(f"0:{transaction.account_addr_hex}")
        total_fee = transaction.total_fees.grams
        lt = transaction.lt
        now = transaction.now
        bag_of_cell = bytes_to_b64str(transaction.cell.to_boc())
        computation_ph = transaction.description.compute_ph
        if computation_ph.type_ == "tr_phase_compute_vm":
            computation_exit_code = computation_ph.exit_code

        action_ph = transaction.description.action

        # check if transaction was not skipped action phase, else None
        if action_ph is not None:
            action_exit_code = action_ph.result_code
        logging.info(f"Transaction with exit codes: {computation_exit_code=}, {action_exit_code=}")
        in_msg = await self.parse_message(transaction.in_msg)
        out_msgs = [await self.parse_message(msg) for msg in transaction.out_msgs]
        result = {
            "account_address": account_address,
            "hash": hash_,
            "compute_phase_code": computation_exit_code,
            "action_phase_code": action_exit_code,
            "total_fee": total_fee,
            "lt": lt,
            "now": now,
            "bag_of_cell": bag_of_cell,
            "in_msg": in_msg,
            "out_msgs": out_msgs,
        }
        return result

    async def parse_message(self, msg: MessageAny) -> RawMessageDTO:
        created_lt = 0
        if isinstance(msg.info, InternalMsgInfo):
            message_type = MessageTypeEnum.internal
            created_lt = msg.info.created_lt
        elif isinstance(msg.info, ExternalMsgInfo):
            message_type = MessageTypeEnum.external
        else:
            logging.error("Unknown message type")
            raise ValueError("Unknown message type")
        src = msg.info.src
        dest = msg.info.dest
        msg_body = msg.body
        msg_body_str = bytes_to_b64str(msg_body.to_boc())
        msg_init = msg.init
        msg_init_str = (
            bytes_to_b64str(msg_init.serialize().to_boc()) if msg_init is not None else None
        )
        cell_body = msg_body.begin_parse()
        op_code = cell_body.load_uint(32)
        logging.info(f"Message op code: {hex(op_code)}")
        return {
            "message_type": message_type,
            "src": src,
            "dest": dest,
            "op_code": op_code,
            "created_lt": created_lt,
            "init": msg_init_str,
            "body": msg_body_str,
        }

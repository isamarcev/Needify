import base64
import json
import logging
from datetime import datetime

from ton.utils import read_address
from tonsdk.boc import Builder, Cell
from tonsdk.contract import Contract
from tonsdk.utils import Address, b64str_to_bytes, to_nano

from src.apps.job_offer.enums import JobOfferOperationCodes
from src.apps.job_offer.schemas import JobOfferDataDTO, MessageDTO
from src.apps.job_offer.utils import decode_b64
from src.core.config import BASE_DIR, config


def find_key_path_and_value(d, target_key, path=None):
    if path is None:
        path = []

    for key, value in d.items():
        current_path = path + [key]
        if key == target_key:
            return current_path, value
        elif isinstance(value, dict):
            result = find_key_path_and_value(value, target_key, current_path)
            if result is not None:
                return result
    return None


class JobOfferContract(Contract):
    def __init__(
        self,
        task_id: int | str,
        title: str,
        description: str,
        price: int,
        jetton_master: str,
        native_master: str,
        **kwargs,
    ):
        if isinstance(task_id, int):
            task_id = str(task_id)
        self.order = task_id
        self.title = title
        self.description = description
        self.price = price
        self.jetton_master = jetton_master
        self.native_master = native_master
        super().__init__(**kwargs)

    @classmethod
    def collect_text_to_cell(cls, text: str) -> Cell:
        encoded_text = text.encode("utf-8")
        b = Builder()
        b.store_bytes(encoded_text[:127])
        if len(encoded_text) > 127:
            b.store_ref(cls.collect_text_to_cell(encoded_text[127:]))
        return b.end_cell()

    def create_state_init(self):
        code_cell = self.get_code_cell()
        data_cell = self.create_data_cell()
        state_init = self.__create_state_init(code_cell, data_cell)
        state_init_hash = state_init.bytes_hash()
        address = Address(str(self.options["wc"]) + ":" + state_init_hash.hex())
        return {
            "code": code_cell,
            "data": data_cell,
            "address": address,
            "state_init": state_init,
        }

    def create_data_cell(self):
        builder_0 = Builder()
        builder_0.store_ref(self.get_system_cell())
        builder_0.store_uint(0, 1)
        builder_0.store_ref(self.collect_text_to_cell(self.title))
        builder_0.store_ref(self.collect_text_to_cell(self.description))
        builder_0.store_int(self.price, 257)

        builder_1 = Builder()
        builder_1.store_ref(self.collect_text_to_cell(self.order))
        builder_1.store_address(Address(self.jetton_master))
        builder_1.store_address(Address(self.native_master))

        builder_0.store_ref(builder_1.end_cell())
        c = builder_0.end_cell()
        return c

    def __create_state_init(self, code, data, library=None, split_depth=None, ticktock=None):
        if library or split_depth or ticktock:
            raise Exception("Library/SplitDepth/Ticktock in state init is not implemented")
        state_init = Cell()
        settings = bytes(
            "".join(
                [
                    "1" if i else "0"
                    for i in [
                        bool(split_depth),
                        bool(ticktock),
                        bool(code),
                        bool(data),
                        bool(library),
                    ]
                ]
            ),
            "utf-8",
        )
        state_init.bits.write_bit_array(settings)
        if code:
            state_init.refs.append(code)
        if data:
            state_init.refs.append(data)
        if library:
            state_init.refs.append(library)
        return state_init

    def create_deploy_message(self):
        cell = Cell()
        timestamp = int(round(datetime.now().timestamp()))
        cell.bits.write_uint(2490013878, 32)
        cell.bits.write_uint(timestamp, 64)
        return cell

    def create_revoke_message(self):
        cell = Cell()
        timestamp = int(round(datetime.now().timestamp()))
        cell.bits.write_uint(JobOfferOperationCodes.REVOKE, 32)
        cell.bits.write_uint(timestamp, 32)
        return cell

    def create_get_job_message(self):
        cell = Cell()
        timestamp = int(round(datetime.now().timestamp()))
        cell.bits.write_uint(JobOfferOperationCodes.GET_JOB, 32)
        cell.bits.write_uint(timestamp, 257)
        return cell

    def create_choose_doer_message(self, doer_address: str):
        cell = Cell()
        cell.bits.write_uint(JobOfferOperationCodes.CHOOSE_DOER, 32)
        cell.bits.write_address(Address(doer_address))
        return cell

    def create_complete_job_message(self):
        cell = Cell()
        timestamp = int(round(datetime.now().timestamp()))
        cell.bits.write_uint(JobOfferOperationCodes.COMPLETE_JOB, 32)
        cell.bits.write_uint(timestamp, 257)
        return cell

    def create_confirm_job_message(self, mark: int | None = None, review: str | None = None):
        timestamp = int(round(datetime.now().timestamp()))
        builder = Builder()
        builder.store_uint(JobOfferOperationCodes.CONFIRM_JOB, 32)
        builder.store_uint(timestamp, 257)
        builder.store_bit(True).store_uint8(mark) if mark is not None else builder.store_bit(False)
        builder.store_bit(True).store_ref(
            self.collect_text_to_cell(review)
        ) if review is not None else builder.store_bit(False)
        return builder.end_cell()

    def get_deploy_message(self) -> MessageDTO:
        state_init = self.create_state_init()
        data = {
            "address": self.address.to_string(
                is_user_friendly=False, is_test_only=True, is_bounceable=False
            ),
            "amount": str(to_nano(config.TON_AMOUNT_TO_DEPLOY, "ton")),
            "payload": base64.urlsafe_b64encode(self.create_deploy_message().to_boc()).decode(),
            "stateInit": base64.urlsafe_b64encode(state_init["state_init"].to_boc()).decode(),
        }
        return data

    def get_revoke_message(self) -> MessageDTO:
        message = {
            "address": self.address.to_string(
                is_user_friendly=False, is_test_only=True, is_bounceable=False
            ),
            "amount": str(to_nano(config.TON_TRANSFER_AMOUNT, "ton")),
            "payload": base64.urlsafe_b64encode(self.create_revoke_message().to_boc()).decode(),
        }
        return message

    def get_get_job_message(self) -> MessageDTO:
        message = {
            "address": self.address.to_string(
                is_user_friendly=False, is_test_only=True, is_bounceable=False
            ),
            "amount": str(to_nano(config.TON_TRANSFER_AMOUNT, "ton")),
            "payload": base64.urlsafe_b64encode(self.create_get_job_message().to_boc()).decode(),
        }
        return message

    def get_complete_job_message(self) -> MessageDTO:
        message = {
            "address": self.address.to_string(
                is_user_friendly=False, is_test_only=True, is_bounceable=False
            ),
            "amount": str(to_nano(config.TON_TRANSFER_AMOUNT, "ton")),
            "payload": base64.urlsafe_b64encode(
                self.create_complete_job_message().to_boc()
            ).decode(),
        }
        return message

    def get_choose_doer_message(self, doer_address: str) -> MessageDTO:
        message = {
            "address": self.address.to_string(
                is_user_friendly=False, is_test_only=True, is_bounceable=False
            ),
            "amount": str(to_nano(config.TON_TRANSFER_AMOUNT, "ton")),
            "payload": base64.urlsafe_b64encode(
                self.create_choose_doer_message(doer_address).to_boc()
            ).decode(),
        }
        return message

    def get_confirm_job_message(
        self, mark: int | None = None, review: str | None = None
    ) -> MessageDTO:
        message = {
            "address": self.address.to_string(
                is_user_friendly=False, is_test_only=True, is_bounceable=False
            ),
            "amount": str(to_nano(config.TON_TRANSFER_AMOUNT, "ton")),
            "payload": base64.urlsafe_b64encode(
                self.create_confirm_job_message(mark, review).to_boc()
            ).decode(),
        }
        return message

    @classmethod
    def get_system_cell(cls):
        with open(BASE_DIR / "contracts/tact_JobOffer.pkg") as file:
            file_json = json.load(file)
            __system = file_json.get("system")
            path_to_key, value = find_key_path_and_value(file_json, "system")
            system_code_value = base64.b64decode(value)
        return Cell.one_from_boc(system_code_value)

    @classmethod
    def get_code_cell(cls) -> str:
        with open(BASE_DIR / "contracts/tact_JobOffer.code.boc", "rb") as file:
            code = Cell.one_from_boc(file.read())
        return code

    @classmethod
    async def parse_job_offer(cls, blockchain_response: dict) -> JobOfferDataDTO:
        stack = blockchain_response["stack"]
        (
            title,
            description,
            price,
            owner,
            doer,
            state,
            balance,
            jetton_wallet,
            native_wallet,
            jetton_balance,
            native_balance,
            appeal_address,
            mark,
            review,
        ) = stack
        logging.info(
            f"All stack data variables: \n {title=}, "
            f"\n {description=}, "
            f"\n {price=}, "
            f"\n {owner=}, "
            f"\n {doer=}, "
            f"\n {state=}, "
            f"\n {balance=}, "
            f"\n {jetton_wallet=}, "
            f"\n {native_wallet=},"
            f"\n {jetton_balance=},"
            f"\n {native_balance=}, "
            f"\n {appeal_address=}, \n {mark}, \n {review} "
        )
        # Title
        title = Cell.one_from_boc(b64str_to_bytes(title[1]["bytes"])).bits.get_top_upped_array()
        title = title.decode().split("\x01")[-1]
        # Description
        first_part_description = decode_b64(description)
        # State
        state = int(state[1], 16)
        # Price
        price = int(price[1], 16)
        # Job Offer jetton wallet
        jetton_wallet_address = read_address(
            Cell.one_from_boc(b64str_to_bytes(jetton_wallet[1]["bytes"]))
        ).to_string(True, True, config.IS_TESTNET)
        # Job Offer native wallet
        native_wallet_address = read_address(
            Cell.one_from_boc(b64str_to_bytes(native_wallet[1]["bytes"]))
        ).to_string(True, True, config.IS_TESTNET)
        # Balance
        balance = int(balance[1], 16)
        # Poster address
        owner_address = read_address(
            Cell.one_from_boc(b64str_to_bytes(owner[1]["bytes"]))
        ).to_string(True, True, config.IS_TESTNET)
        # Doer address
        try:
            doer = read_address(Cell.one_from_boc(b64str_to_bytes(doer[1]["bytes"]))).to_string(
                True, True, config.IS_TESTNET
            )
        except KeyError:
            doer = None
        # Appeal address
        try:
            appeal_address = read_address(
                Cell.one_from_boc(b64str_to_bytes(appeal_address[1]["bytes"]))
            ).to_string(True, True, True)
        except KeyError:
            appeal_address = None
        # Mark
        try:
            mark = int(mark[1], 16)
        except TypeError:
            mark = None
        # Review
        review = decode_b64(review)
        # Jetton balance
        jetton_balance = int(jetton_balance[1], 16)
        # Native balance
        native_balance = int(native_balance[1], 16)
        response = {
            "title": title,
            "description": first_part_description,
            "price": price,
            "owner": owner_address,
            "doer": doer,
            "state": state,
            "balance": balance,
            "jetton_wallet": jetton_wallet_address,
            "native_wallet": native_wallet_address,
            "jetton_balance": jetton_balance,
            "native_balance": native_balance,
            "appeal_address": appeal_address,
            "mark": mark,
            "review": review,
        }
        return response

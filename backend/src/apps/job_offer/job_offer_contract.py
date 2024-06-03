import base64
import json
from datetime import datetime

from tonsdk.boc import Builder, Cell
from tonsdk.contract import Contract
from tonsdk.utils import Address, to_nano

from src.core.config import BASE_DIR


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

    def get_deploy_message(self):
        state_init = self.create_state_init()
        data = {
            "address": self.address.to_string(
                is_user_friendly=False, is_test_only=True, is_bounceable=False
            ),
            "amount": str(to_nano(0.5, "ton")),
            "payload": base64.urlsafe_b64encode(self.create_deploy_message().to_boc()).decode(),
            "stateInit": base64.urlsafe_b64encode(state_init["state_init"].to_boc()).decode(),
        }
        return data

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

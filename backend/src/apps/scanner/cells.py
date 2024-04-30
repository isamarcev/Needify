# create cell object
from tonsdk.contract import Address
from tonsdk.boc import Cell, begin_cell

address = "UQBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8Itwbjl1"
contract_address = Address(address)
message = begin_cell().store_uint(15, 32).store_address()
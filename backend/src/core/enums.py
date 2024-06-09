from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value

    __repr__ = __str__


class TransactionStatusExitCodes(Enum):
    SUCCESS = 0
    INVALID_TRANSACTION = 1
    INSUFFICIENT_FUNDS = 2
    UNKNOWN_ERROR = 3

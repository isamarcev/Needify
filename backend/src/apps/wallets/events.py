from src.core.enums import StrEnum


class WalletTopicsEnum(StrEnum):
    FOUNDED_DEPOSIT_WALLET = "FOUNDED_DEPOSIT_WALLET"

    @classmethod
    def topics_list(cls):
        return [topic.value for topic in cls]

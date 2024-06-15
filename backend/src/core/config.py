import contextvars
import pathlib
from uuid import uuid4

from dotenv import load_dotenv

# from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseSettings

from src.apps.utils.wallet import get_wallet_info_by_mnemonic

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
PROJECT_DIR = BASE_DIR / "app"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

CONTEXT_ID = contextvars.ContextVar("context_id", default=str(uuid4()))

load_dotenv(BASE_DIR / ".env")


class BaseConfig(BaseSettings):
    # BOT_TOKEN: str
    REDIS_URL: str
    MONGO_DB_URL: str
    MONGO_DB_NAME: str
    HD_WALLET_MNEMONIC: str
    HD_WALLET_ADDRESS: str

    WORKCHAIN: int = 0
    IS_TESTNET: bool = False

    AMOUNT_TON_TO_DEPLOY: float = 0.05
    NATIVE_JETTON_CONTENT_URL: str
    LITESERVER_INDEX: int = 2
    TON_CENTER_URL: str
    TON_CENTER_API_KEY: str

    NATIVE_CURRENCY_PRICE_TO_DEPLOY: float = 100

    TON_AMOUNT_TO_DEPLOY: float = 0.5
    TON_TRANSFER_AMOUNT: float = 0.3
    JETTON_TRANSFER_FORWARD_FEE: float = 0.2

    # TIME
    TON_CONNECT_VALID_TIME: int = 3600

    # KAFKA
    KAFKA_BOOTSTRAP_SERVERS: list[str]

    MANIFEST_URL: str

    UPDATE_LAST_SCANNED_BLOCK: bool = False

    class Config:
        env_file = ".env"

    @property
    def hd_wallet_mnemonic_list(self):
        return self.HD_WALLET_MNEMONIC.split()


class SecurityConfig(BaseSettings):
    TOKEN_SECRET_KEY: str
    TOKEN_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


config = BaseConfig()

security_settings = SecurityConfig()

hd_wallet_info = get_wallet_info_by_mnemonic(
    config.hd_wallet_mnemonic_list,
    config.WORKCHAIN,
    is_testnet=config.IS_TESTNET,
)

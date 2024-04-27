import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = pathlib.Path(__file__).parent.parent.parent
PROJECT_DIR = BASE_DIR / "app"

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="allow"
    )
    BOT_TOKEN: str
    REDIS_URL: str
    MONGO_DB_URL: str
    MONGO_DB_NAME: str


class SecurityConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="allow"
    )
    TOKEN_SECRET_KEY: str
    TOKEN_ALGORITHM: str = "HS256"


config = BaseConfig()

security_settings = SecurityConfig()

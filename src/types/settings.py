from pydantic_settings import BaseSettings
from pydantic import SecretStr, PostgresDsn


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    DATABASE_URL: PostgresDsn


settings = Settings()

from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr = "6287767778:AAH7s-UvZxIMEmE7F4F6DAsxF-y7iQeJF18"


settings = Settings()

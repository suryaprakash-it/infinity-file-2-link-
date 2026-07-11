from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    API_ID: int = Field(...)
    API_HASH: str = Field(...)
    BOT_TOKEN: str = Field(...)

    # MongoDB
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017/infinity_share"
    )

    # Website
    SERVER_URL: str = Field(
        default="http://localhost:8000"
    )

    # Security
    SECRET_KEY: str = Field(...)

    # Optional
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    MAX_DOWNLOAD_CONNECTIONS: int = Field(default=100)


settings = Settings()
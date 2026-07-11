import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_ID: int = int(os.getenv("API_ID", 1234567))
    API_HASH: str = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "your_bot_token")
    
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/infinity_share")
    SERVER_URL: str = os.getenv("SERVER_URL", "http://localhost:8000")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretadminpasskey")

settings = Settings()

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Transport Document Expiration Monitor"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./transport_test.db")
    WHATSAPP_API_TOKEN: str = os.getenv("WHATSAPP_API_TOKEN", "mock-token")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "mock-phone-id")
    WHATSAPP_VERSION: str = "v18.0"

settings = Settings()
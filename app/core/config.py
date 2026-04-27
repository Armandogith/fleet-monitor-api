import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Transport Document Expiration Monitor"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./transport_test.db")
    SMSDEV_API_KEY: str = os.getenv("SMSDEV_API_KEY", "")
    WHATSAPP_VERSION: str = os.getenv("WHATSAPP_VERSION", "v18.0")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_API_TOKEN: str = os.getenv("WHATSAPP_API_TOKEN", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

settings = Settings()
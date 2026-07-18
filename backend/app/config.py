from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Firebase Settings
    FIREBASE_PROJECT_ID: str = "softwarereliability"
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = "firebase-service-account.json"

    # File Upload Directory
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
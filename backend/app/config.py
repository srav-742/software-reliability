from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]

    DATABASE_URL: str = "sqlite:///./software_reliability.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+psycopg2://", 1)
            elif v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    # JWT Settings
    SECRET_KEY: str = "8e6c46a6f1d2df894a44b4c73bf5408a28723226db9783f6f1947b744a5b045e"

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Firebase Settings
    FIREBASE_PROJECT_ID: str = "softwarereliability"
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = "firebase-service-account.json"

    # File Upload Directory
    UPLOAD_DIR: str = "uploads"

    # Operational & Monitoring Settings
    SENTRY_DSN: Optional[str] = None
    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
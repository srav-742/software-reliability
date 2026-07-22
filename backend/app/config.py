import json
from typing import Any, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: Any = ["*"]
    CORS_ORIGIN_REGEX: Optional[str] = r"https://.*\.vercel\.app"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v_str = v.strip().strip("'\"")
            if not v_str:
                return ["*"]
            if v_str.startswith("["):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        return [
                            item.strip().strip("'\"").rstrip("/")
                            for item in parsed
                            if isinstance(item, str) and item.strip()
                        ]
                except Exception:
                    pass
            return [
                item.strip().strip("'\"").rstrip("/")
                for item in v_str.split(",")
                if item.strip()
            ]
        if isinstance(v, list):
            return [
                item.strip().strip("'\"").rstrip("/")
                for item in v
                if isinstance(item, str) and item.strip()
            ]
        return ["*"]

    DATABASE_URL: str = "sqlite:///./software_reliability.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            v_clean = v.strip().strip("'\"")
            if v_clean.startswith("postgres://"):
                return v_clean.replace("postgres://", "postgresql+psycopg2://", 1)
            elif v_clean.startswith("postgresql://"):
                return v_clean.replace("postgresql://", "postgresql+psycopg2://", 1)
            return v_clean
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
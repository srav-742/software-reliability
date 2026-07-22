from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine_kwargs = {
    "echo": False if settings.ENVIRONMENT == "production" else True,
    "future": True,
    "connect_args": connect_args,
}

if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
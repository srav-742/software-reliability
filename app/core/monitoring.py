import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.core.logging import logger


def init_sentry() -> None:
    """Initializes Sentry Error Tracking if SENTRY_DSN is provided."""
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
        )
        logger.info("Sentry SDK successfully initialized", extra={"environment": settings.ENVIRONMENT})


def init_monitoring(app: FastAPI) -> None:
    """Instruments FastAPI application with Prometheus metrics endpoint at /metrics."""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        env_var_name="ENABLE_PROMETHEUS_METRICS",
        excluded_handlers=["/metrics", "/health", "/docs", "/openapi.json"]
    )
    instrumentator.instrument(app).expose(app, include_in_schema=False, tags=["Monitoring"])
    logger.info("Prometheus metrics instrumentation enabled", extra={"endpoint": "/metrics"})

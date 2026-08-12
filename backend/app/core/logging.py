import logging
import sys
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pythonjsonlogger import jsonlogger

from app.config import settings


class CustomConsoleFormatter(logging.Formatter):
    """Custom formatter for local development console logging."""
    def format(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "environment"):
            record.environment = settings.ENVIRONMENT
        return super().format(record)


def setup_logging() -> logging.Logger:
    """Configures logging: structured JSON in production, clean readable text in development/staging."""
    log_handler = logging.StreamHandler(sys.stdout)
    
    if settings.ENVIRONMENT == "production":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(environment)s",
            timestamp=True
        )
    else:
        # Standard human-readable console logging for development
        formatter = CustomConsoleFormatter(
            "[%(asctime)s] %(levelname)-8s in %(name)s: %(message)s [req_id=%(request_id)s]"
        )
        
    log_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [log_handler]
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Silence noisy loggers
    logging.getLogger("uvicorn.access").handlers = [log_handler]
    
    logger = logging.getLogger("app")
    logger.info("Logging initialized", extra={"environment": settings.ENVIRONMENT})
    return logger


logger = logging.getLogger("app")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware that injects an X-Request-ID header into requests and logs response times."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"{request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "method": request.method,
                "path": request.url.path,
                "environment": settings.ENVIRONMENT,
            }
        )
        return response

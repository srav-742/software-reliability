import logging
import sys
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logging() -> logging.Logger:
    """Configures structured JSON logging for the application."""
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(environment)s",
        timestamp=True
    )
    log_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [log_handler]
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Silence noisy loggers
    logging.getLogger("uvicorn.access").handlers = [log_handler]
    
    logger = logging.getLogger("app")
    logger.info("Structured JSON logging initialized", extra={"environment": settings.ENVIRONMENT})
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

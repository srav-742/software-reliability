from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.config import settings
from app.core.logging import setup_logging, RequestIdMiddleware
from app.core.rate_limit import limiter
from app.core.monitoring import init_sentry, init_monitoring

# Initialize structured logging and Sentry error tracking
logger = setup_logging()
init_sentry()

app = FastAPI(
    title="Software Reliability API",
    description="API backend for Software Reliability prediction, registry, and analysis.",
    version="1.0.0",
)

# Rate limiting state & exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request ID correlation middleware
app.add_middleware(RequestIdMiddleware)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics setup
init_monitoring(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """Root redirect message pointing to API documentation."""
    return {
        "message": "Welcome to the Software Reliability API.",
        "documentation": "/docs",
        "health_check": "/api/v1/health"
    }

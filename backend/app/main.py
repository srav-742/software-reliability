from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

app = FastAPI(
    title="Software Reliability API",
    description="API backend for Software Reliability prediction, registry, and analysis.",
    version="1.0.0",
)

# CORS middleware configuration (crucial for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include api_router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """Root redirect message pointing to API documentation."""
    return {
        "message": "Welcome to the Software Reliability API.",
        "documentation": "/docs",
        "health_check": "/api/v1/health"
    }

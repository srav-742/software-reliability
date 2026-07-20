from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.database.session import SessionLocal
from app.config import settings

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def health_check():
    """Simple API health check endpoint."""
    return {
        "status": "healthy",
        "service": "software-reliability-backend",
        "environment": settings.ENVIRONMENT
    }


@router.get("/live")
def liveness_check():
    """Liveness probe: returns 200 if backend container is running."""
    return {"status": "alive"}


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe: checks database connection before accepting traffic."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

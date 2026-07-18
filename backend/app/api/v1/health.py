from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check():
    """Simple API health check endpoint."""
    return {"status": "healthy", "service": "software-reliability-backend"}

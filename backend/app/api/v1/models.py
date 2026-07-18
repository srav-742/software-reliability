"""
Model Registry API endpoint for Software Reliability.

GET /api/v1/models — List all registered ML models.
GET /api/v1/models/active — Get the currently active model.
PUT /api/v1/models/{model_id}/activate — Set a model as active.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.model_service import model_service

router = APIRouter()


@router.get("/models")
def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all registered ML models with their performance metrics.
    """
    return model_service.list_models(db)


@router.get("/models/active")
def get_active_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the currently active ML model used for predictions.
    """
    model = model_service.get_active_model(db)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active model found. Please train models first.",
        )
    return model


@router.put("/models/{model_id}/activate")
def activate_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Set a specific model as the active inference model.
    Deactivates all other models.
    """
    result = model_service.set_active_model(db, model_id=model_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found.",
        )
    return {"status": "success", "message": f"Model {model_id} is now active.", "model": result}

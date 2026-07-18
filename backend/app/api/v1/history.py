"""
Prediction History API endpoint for Software Reliability.

GET /api/v1/history — Get all prediction history for the current user's projects.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.prediction import Prediction
from app.models.project import Project
from app.schemas.prediction import PredictionDBResponse

router = APIRouter()


@router.get("/history", response_model=List[PredictionDBResponse])
def get_all_predictions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all prediction records across all of the current user's projects.
    Sorted by most recent first.
    """
    predictions = (
        db.query(Prediction)
        .join(Project, Prediction.project_id == Project.id)
        .filter(Project.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return predictions

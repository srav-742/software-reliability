"""
Prediction API endpoint for Software Reliability.

POST /api/v1/projects/{project_id}/predict — Run reliability prediction.
GET /api/v1/projects/{project_id}/predictions — Get prediction history.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.prediction import PredictionResponse, ReliabilityStats, PredictionDBResponse
from app.services.prediction_service import prediction_service
from app.repositories.project_repository import project_repository
from app.repositories.prediction_repository import prediction_repository
from app.ml.inference.model_loader import is_model_available

router = APIRouter()


@router.post(
    "/projects/{project_id}/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
)
def predict_project_reliability(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run ML-based reliability prediction for a project.

    Prerequisites:
        1. Project must exist and belong to the current user.
        2. Project must have been analyzed (metrics extracted).
        3. A trained model must exist (run POST /api/v1/train first).

    Returns:
        Failure probability, risk level, reliability statistics (MTBF, λ, R(t)),
        and actionable refactoring recommendations.
    """
    # Validate project ownership
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check if model is available
    if not is_model_available():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No trained model available. Please train a model first via POST /api/v1/train",
        )

    try:
        result = prediction_service.predict_project(db=db, project_id=project_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )

    return PredictionResponse(
        project_id=result["project_id"],
        predicted_label=result["predicted_label"],
        failure_probability=result["failure_probability"],
        risk_level=result["risk_level"],
        confidence_score=result["confidence_score"],
        reliability_stats=ReliabilityStats(**result["reliability_stats"]),
        model_used=result["model_used"],
        recommendations=result["recommendations"],
    )


@router.get(
    "/projects/{project_id}/predictions",
    response_model=List[PredictionDBResponse],
)
def get_prediction_history(
    project_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get prediction history for a specific project.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return prediction_repository.get_by_project(
        db, project_id=project_id, skip=skip, limit=limit
    )

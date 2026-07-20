"""
Explanation API endpoint for Software Reliability.

GET /api/v1/projects/{project_id}/explain — SHAP feature attribution & recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.prediction import ExplanationResponse, ShapFeatureContribution
from app.services.prediction_service import prediction_service
from app.repositories.project_repository import project_repository
from app.ml.inference.model_loader import is_model_available

router = APIRouter()


@router.get(
    "/projects/{project_id}/explain",
    response_model=ExplanationResponse,
)
def explain_prediction(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get SHAP-based explanation for a project's reliability prediction.

    Returns:
        - Top risk factors with SHAP values
        - Full SHAP feature attribution map
        - Feature importance ranking
        - Actionable refactoring recommendations
    """
    # Validate project ownership
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not is_model_available():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No trained model available. Please train a model first.",
        )

    try:
        result = prediction_service.explain_project(db=db, project_id=project_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation failed: {str(e)}",
        )

    top_factors = [
        ShapFeatureContribution(**factor)
        for factor in result["top_risk_factors"]
    ]

    return ExplanationResponse(
        project_id=result["project_id"],
        model_used=result["model_used"],
        top_risk_factors=top_factors,
        shap_values=result["shap_values"],
        feature_importance=result["feature_importance"],
        recommendations=result["recommendations"],
    )

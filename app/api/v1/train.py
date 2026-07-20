"""
Training API endpoint for Software Reliability ML pipeline.

POST /api/v1/train — Trigger model training across all 7 algorithms.
GET /api/v1/train/history — Get training history for the current user.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.training import TrainingRequest, TrainingResponse, ModelMetrics, ModelResult, TrainingRunResponse
from app.services.training_service import training_service
from app.repositories.training_repository import training_repository

router = APIRouter()


@router.post("/train", response_model=TrainingResponse, status_code=status.HTTP_201_CREATED)
def train_models(
    request: TrainingRequest = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger ML model training for software reliability prediction.

    Trains all 7 algorithms (or specified subset), evaluates them,
    selects the best model by F1 score, and persists it.

    Optional body:
        - algorithms: list of specific algorithms to train
        - test_size: fraction of data for testing (default 0.2)
        - dataset_path: path to custom CSV dataset (default: synthetic)
    """
    if request is None:
        request = TrainingRequest()

    try:
        result = training_service.run_training(
            db=db,
            user_id=current_user.id,
            algorithms=request.algorithms,
            dataset_path=request.dataset_path,
            test_size=request.test_size,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}",
        )

    # Build response
    all_model_results = []
    for r in result["all_results"]:
        all_model_results.append(
            ModelResult(
                algorithm=r["algorithm"],
                metrics=ModelMetrics(**r["metrics"]),
                training_time=r["training_time"],
                error=r.get("error"),
            )
        )

    return TrainingResponse(
        status=result["status"],
        message=result["message"],
        dataset_size=result["dataset_size"],
        best_algorithm=result["best_algorithm"] or "none",
        best_metrics=ModelMetrics(**result["best_metrics"]) if result["best_metrics"] else ModelMetrics(
            accuracy=0, precision=0, recall=0, f1_score=0, roc_auc=0
        ),
        all_results=all_model_results,
        model_paths=result["model_paths"],
    )


@router.get("/train/history", response_model=List[TrainingRunResponse])
def get_training_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get training run history for the current user.
    """
    return training_repository.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

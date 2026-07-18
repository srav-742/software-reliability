from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.metrics import MetricResponse, MetricCreate
from app.repositories.project_repository import project_repository
from app.repositories.metrics_repository import metrics_repository
from app.feature_extraction.extractor import FeatureExtractor

router = APIRouter()


@router.post("/projects/{project_id}/analyze", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
def analyze_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger automated feature extraction and code parsing for a saved project.
    Extracts lines of code, cyclomatic complexity, dependencies, AST metrics, and saves to database.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Resolve source path (zip path or direct directory)
    source_path = project.source_code_path

    # Run Feature Extraction
    extracted_features = FeatureExtractor.extract_from_path(source_path)

    # Build DB payload
    metric_in = MetricCreate(
        project_id=project.id,
        **extracted_features
    )

    # Save metrics to DB
    saved_metric = metrics_repository.create(db, obj_in=metric_in)
    return saved_metric

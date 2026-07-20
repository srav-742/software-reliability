from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.metrics import MetricResponse, MetricCreate
from app.repositories.project_repository import project_repository
from app.repositories.metrics_repository import metrics_repository

router = APIRouter()


@router.get("/projects/{project_id}/metrics", response_model=MetricResponse)
def read_project_metrics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the latest extracted metrics for a specific project.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    metric = metrics_repository.get_by_project(db, project_id=project_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics found for this project. Please run analysis first."
        )

    return metric


@router.post("/projects/{project_id}/metrics", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
def create_project_metric(
    project_id: int,
    metric_in: MetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually submit or update metrics for a specific project.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    metric_in.project_id = project_id
    return metrics_repository.create(db, obj_in=metric_in)

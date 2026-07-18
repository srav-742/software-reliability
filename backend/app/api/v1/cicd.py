from typing import List, Optional
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.cicd import CICDScanResponse, CICDScanSummaryResponse
from app.services.cicd_service import cicd_service
from app.repositories.cicd_repository import cicd_repository

router = APIRouter()


@router.post("/scan", status_code=status.HTTP_201_CREATED)
def trigger_cicd_scan(
    source_code_file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    project_name: Optional[str] = Form(None),
    commit_sha: Optional[str] = Form(None),
    branch: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    pass_threshold: float = Form(50.0),
    warn_threshold: float = Form(80.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Atomic CI/CD Build Scan endpoint for GitHub Actions and build pipelines.

    Workflow:
    1. Upload source code archive (.zip).
    2. Extract codebase metrics (LOC, Cyclomatic Complexity, AST).
    3. Run ML Reliability Prediction model (failure probability, risk score).
    4. Enforce Policy Thresholds (Pass < 50%, Fail > 80%).
    5. Generate Markdown report for GitHub Step Summaries.
    6. Return risk score, status (PASS, WARN, FAIL), and exit_code (0 or 1).
    """
    try:
        scan_result = cicd_service.process_scan(
            db=db,
            user=current_user,
            source_code_file=source_code_file,
            project_id=project_id,
            project_name=project_name,
            commit_sha=commit_sha,
            branch=branch,
            author=author,
            pass_threshold=pass_threshold,
            warn_threshold=warn_threshold,
        )
        return scan_result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CI/CD Scan execution failed: {str(e)}",
        )


@router.get("/scans", response_model=List[CICDScanResponse])
def get_user_scans(
    skip: int = 0,
    limit: int = 50,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve CI/CD scan pipeline execution history.
    """
    if project_id:
        return cicd_repository.get_project_scans(db, project_id=project_id, skip=skip, limit=limit)
    return cicd_repository.get_user_scans(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/scans/{scan_id}", response_model=CICDScanResponse)
def get_scan_details(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve full details for a specific CI/CD scan.
    """
    scan = cicd_repository.get_by_id(db, scan_id=scan_id)
    if not scan or scan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found or access denied"
        )
    return scan

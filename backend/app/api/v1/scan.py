"""
API Key Scan endpoints.
Allows users to trigger scans on uploaded projects to detect and validate
embedded API keys.
"""

import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.api_key_scan import (
    ApiKeyScanResponse,
    ApiKeyScanSummaryResponse,
)
from app.repositories.project_repository import project_repository
from app.repositories.api_key_scan_repository import api_key_scan_repository
from app.services.api_key_scanner import scan_and_validate

router = APIRouter()


@router.post(
    "/projects/{project_id}/scan-keys",
    response_model=ApiKeyScanResponse,
    status_code=status.HTTP_201_CREATED,
)
def scan_project_keys(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger an API key scan on the uploaded project source code.
    Detects API keys from .env, config files, and source code,
    then validates each key against its provider's API.
    """
    # Verify project ownership
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Verify source code exists
    source_path = project.source_code_path
    if not source_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No source code uploaded for this project. Please upload a project file first.",
        )

    # Run the scan + validation pipeline
    try:
        scan_result = asyncio.run(scan_and_validate(source_path))
    except RuntimeError:
        # If there's already a running event loop (e.g., in async context)
        loop = asyncio.get_event_loop()
        scan_result = loop.run_until_complete(scan_and_validate(source_path))

    # Persist scan summary to database
    scan_record = api_key_scan_repository.create_scan(
        db=db,
        project_id=project.id,
        total_keys_found=scan_result.total_keys_found,
        valid_keys=scan_result.valid_keys,
        invalid_keys=scan_result.invalid_keys,
        unknown_keys=scan_result.unknown_keys,
        scan_status=scan_result.scan_status,
    )

    # Persist individual detected keys
    if scan_result.detected_keys:
        keys_data = [
            {
                "provider": k.provider,
                "key_masked": k.masked_key,
                "file_path": k.file_path,
                "line_number": k.line_number,
                "status": k.status,
                "error_message": " | ".join(k.reasons) if k.reasons else k.error_message,
                "failure_chance": k.failure_chance,
                "risk_level": k.risk_level,
            }
            for k in scan_result.detected_keys
        ]
        api_key_scan_repository.add_detected_keys_bulk(db, scan_record.id, keys_data)

    # Refresh to load relationships
    db.refresh(scan_record)
    return scan_record


@router.get(
    "/projects/{project_id}/scan-keys",
    response_model=ApiKeyScanResponse,
)
def get_latest_scan(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the most recent API key scan results for a project.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    scan = api_key_scan_repository.get_latest_scan(db, project_id=project_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No scan results found. Trigger a scan first.",
        )

    return scan


@router.get(
    "/projects/{project_id}/scan-keys/history",
    response_model=List[ApiKeyScanSummaryResponse],
)
def get_scan_history(
    project_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the full scan history for a project.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return api_key_scan_repository.get_scan_history(
        db, project_id=project_id, skip=skip, limit=limit,
    )

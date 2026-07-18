from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from app.repositories.project_repository import project_repository
from app.services.project_service import project_service

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_name: str = Form(...),
    language: str = Form("Python"),
    framework: Optional[str] = Form(None),
    repository_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    source_code_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new project.
    Accepts form parameters and an optional source code file upload.
    """
    source_code_path = None
    if source_code_file and source_code_file.filename:
        try:
            source_code_path = project_service.save_source_code(source_code_file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save source code file: {str(e)}"
            )

    project_in = ProjectCreate(
        project_name=project_name,
        language=language,
        framework=framework,
        repository_url=repository_url,
        description=description,
    )

    return project_repository.create(
        db, obj_in=project_in, user_id=current_user.id, source_code_path=source_code_path
    )


@router.get("/", response_model=List[ProjectResponse])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all projects belonging to the current user.
    """
    return project_repository.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed information about a specific project.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_name: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    framework: Optional[str] = Form(None),
    repository_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    status_field: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    source_code_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update project details. If a new source code file is uploaded, the old file is deleted.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Save new file and clean up old file if a new file is uploaded
    source_code_path = None
    if source_code_file and source_code_file.filename:
        try:
            # Delete old code if it exists
            if project.source_code_path:
                project_service.delete_source_code(project.source_code_path)
            
            # Save new source code
            source_code_path = project_service.save_source_code(source_code_file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save source code file: {str(e)}"
            )

    project_update = ProjectUpdate(
        project_name=project_name if project_name is not None else project.project_name,
        language=language if language is not None else project.language,
        framework=framework if framework is not None else project.framework,
        repository_url=repository_url if repository_url is not None else project.repository_url,
        description=description if description is not None else project.description,
        version=version if version is not None else project.version,
        status=status_field if status_field is not None else project.status,
    )

    return project_repository.update(
        db, db_obj=project, obj_in=project_update, source_code_path=source_code_path
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a project. Also deletes associated source code from disk.
    """
    project = project_repository.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Delete source code first if it exists
    if project.source_code_path:
        project_service.delete_source_code(project.source_code_path)

    project_repository.delete(db, id=project_id)
    return

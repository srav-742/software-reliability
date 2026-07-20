from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse
from app.repositories.api_key_repository import api_key_repository

router = APIRouter()


@router.post("/", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    key_in: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a new API key for CI/CD pipeline integration (e.g. GitHub Actions).
    The full raw_key is only returned ONCE in this response.
    """
    key_obj, raw_key = api_key_repository.create(db, user_id=current_user.id, name=key_in.name)

    return ApiKeyCreatedResponse(
        id=key_obj.id,
        name=key_obj.name,
        key_prefix=key_obj.key_prefix,
        created_at=key_obj.created_at,
        last_used_at=key_obj.last_used_at,
        raw_key=raw_key,
    )


@router.get("/", response_model=List[ApiKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all active API keys for the current user.
    """
    return api_key_repository.get_user_keys(db, user_id=current_user.id)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Revoke/Deactivate an API key.
    """
    success = api_key_repository.revoke(db, user_id=current_user.id, key_id=key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key not found or already revoked"
        )
    return

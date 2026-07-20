from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.models.user import User
from app.repositories.api_key_repository import api_key_repository

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    token: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to retrieve current user via either:
    1. X-API-Key header (for automated CI/CD runners & integrations)
    2. Bearer JWT token (for standard web frontend sessions)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Provide a valid Bearer token or X-API-Key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Try X-API-Key authentication
    if x_api_key:
        user_from_key = api_key_repository.validate_key(db, x_api_key)
        if user_from_key and user_from_key.is_active:
            return user_from_key
        raise credentials_exception

    # 2. Try Bearer JWT authentication
    if not token or not token.credentials:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.firebase import sync_register_firebase_user, create_firebase_custom_token, is_firebase_initialized
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user:
    1. Check if user already exists.
    2. Hash password with bcrypt.
    3. Save to database.
    4. Sync registration with Firebase Auth (fail-safe).
    """
    logger.info(f"[REGISTER] Received registration request for email: {user_in.email}")

    # Check if user already exists
    try:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
    except Exception as e:
        logger.error(f"[REGISTER] Database query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during registration: {str(e)}"
        )

    if existing_user:
        logger.warning(f"[REGISTER] User with email {user_in.email} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # Hash the password
    hashed_password = get_password_hash(user_in.password)

    # Create local user
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=hashed_password,
        role=user_in.role or "developer"
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"[REGISTER] Successfully saved user {user_in.email} to PostgreSQL with id={new_user.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"[REGISTER] Failed to save user to PostgreSQL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save user to database: {str(e)}"
        )

    # Synchronize with Firebase Auth (fail-safe)
    # If this fails (e.g. Firebase credentials not supplied), it logs a warning but registration completes.
    fb_uid = sync_register_firebase_user(
        email=new_user.email,
        password=user_in.password,
        display_name=new_user.full_name
    )
    if fb_uid:
        logger.info(f"[REGISTER] Firebase sync successful for {user_in.email}, Firebase UID: {fb_uid}")
    else:
        logger.warning(f"[REGISTER] Firebase sync skipped or failed for {user_in.email}")

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user:
    1. Verify credentials in database.
    2. Create local access token (JWT).
    3. Create Firebase Custom Token (fail-safe).
    """
    logger.info(f"[LOGIN] Received login request for email: {login_in.email}")

    try:
        user = db.query(User).filter(User.email == login_in.email).first()
    except Exception as e:
        logger.error(f"[LOGIN] Database query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during login: {str(e)}"
        )

    if not user or not verify_password(login_in.password, user.password_hash):
        logger.warning(f"[LOGIN] Invalid credentials for email: {login_in.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )

    # Generate backend access token
    access_token = create_access_token(user.id)
    logger.info(f"[LOGIN] JWT token generated for user id={user.id}")

    # Synchronize with Firebase Auth (fail-safe) to ensure user exists in Firebase Auth
    sync_register_firebase_user(
        email=user.email,
        password=login_in.password,
        display_name=user.full_name
    )

    # Generate Firebase Custom Token (fail-safe)
    firebase_token = create_firebase_custom_token(str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "firebase_token": firebase_token,
        "user": user
    }


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieve current authenticated user's profile.
    This is a protected route.
    """
    return current_user


@router.get("/debug-health")
def debug_health(db: Session = Depends(get_db)):
    """
    Debug endpoint to verify database connectivity and Firebase status.
    Hit this from your browser to check if the backend can reach PostgreSQL and Firebase.
    """
    result = {
        "status": "ok",
        "database": {"connected": False, "url_prefix": "unknown", "user_count": None, "error": None},
        "firebase": {"initialized": is_firebase_initialized, "error": None},
        "config": {
            "database_url_set": bool(settings.DATABASE_URL and settings.DATABASE_URL != "sqlite:///./software_reliability.db"),
            "database_url_prefix": settings.DATABASE_URL[:30] + "..." if len(settings.DATABASE_URL) > 30 else settings.DATABASE_URL,
            "environment": settings.ENVIRONMENT,
        }
    }

    # Test database connectivity
    try:
        db.execute(text("SELECT 1"))
        result["database"]["connected"] = True

        user_count = db.query(User).count()
        result["database"]["user_count"] = user_count
        logger.info(f"[DEBUG-HEALTH] DB connected. User count: {user_count}")
    except Exception as e:
        result["database"]["error"] = str(e)
        result["status"] = "degraded"
        logger.error(f"[DEBUG-HEALTH] DB connection failed: {e}")

    # Test Firebase status
    if not is_firebase_initialized:
        result["firebase"]["error"] = "Firebase Admin SDK not initialized. Check FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_PRIVATE_KEY env vars."
        result["status"] = "degraded"

    return result

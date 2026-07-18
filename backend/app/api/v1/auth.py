from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.firebase import sync_register_firebase_user, create_firebase_custom_token

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
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
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
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Synchronize with Firebase Auth (fail-safe)
    # If this fails (e.g. Firebase credentials not supplied), it logs a warning but registration completes.
    sync_register_firebase_user(
        email=new_user.email,
        password=user_in.password,
        display_name=new_user.full_name
    )

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user:
    1. Verify credentials in database.
    2. Create local access token (JWT).
    3. Create Firebase Custom Token (fail-safe).
    """
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
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

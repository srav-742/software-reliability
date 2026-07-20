import logging
import os
from typing import Union
import firebase_admin
from firebase_admin import credentials, auth

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

firebase_app = None
is_firebase_initialized = False

# Try initializing Firebase Admin SDK
try:
    firebase_admin.get_app()
    is_firebase_initialized = True
    logger.info("Firebase Admin is already initialized.")
except ValueError:
    try:
        sa_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
        if sa_path and os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)
            firebase_app = firebase_admin.initialize_app(cred)
            is_firebase_initialized = True
            logger.info("Firebase Admin initialized with service account certificate.")
        else:
            # Fallback initialization using project ID
            firebase_app = firebase_admin.initialize_app(
                options={"projectId": settings.FIREBASE_PROJECT_ID}
            )
            is_firebase_initialized = True
            logger.warning(
                f"Firebase Admin initialized using projectId={settings.FIREBASE_PROJECT_ID} "
                "without service account file. Custom token generation might fail if credentials are not loaded."
            )
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        is_firebase_initialized = False


def sync_register_firebase_user(
    email: str, password: str, display_name: str
) -> Union[str, None]:
    """
    Creates a user in Firebase Auth.
    If the user already exists in Firebase, retrieves the existing Firebase UID.
    Returns Firebase UID if successful, otherwise None.
    """
    if not is_firebase_initialized:
        logger.warning("Firebase Admin is not initialized. Skipping Firebase user registration.")
        return None

    try:
        try:
            fb_user = auth.get_user_by_email(email)
            logger.info(f"User with email {email} already exists in Firebase with UID {fb_user.uid}.")
            return fb_user.uid
        except auth.UserNotFoundError:
            # Password must be at least 6 characters in Firebase Auth
            fb_pwd = password if len(password) >= 6 else "fallback_dummy_pwd_123"
            fb_user = auth.create_user(
                email=email,
                password=fb_pwd,
                display_name=display_name
            )
            logger.info(f"Successfully registered user {email} in Firebase. UID: {fb_user.uid}")
            return fb_user.uid
    except Exception as e:
        logger.error(f"Error registering user in Firebase: {e}")
        return None


def create_firebase_custom_token(user_id: str) -> Union[str, None]:
    """
    Generates a Firebase Custom Token for a user ID.
    Returns the custom token string if successful, otherwise None.
    """
    if not is_firebase_initialized:
        logger.warning("Firebase Admin is not initialized. Skipping custom token generation.")
        return None

    try:
        # Create a custom token using str(user_id) as the UID
        custom_token = auth.create_custom_token(str(user_id))
        if isinstance(custom_token, bytes):
            return custom_token.decode("utf-8")
        return custom_token
    except Exception as e:
        logger.error(f"Error creating Firebase custom token: {e}")
        return None

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
        sa_json_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        sa_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
        private_key = os.getenv("FIREBASE_PRIVATE_KEY")

        logger.info(f"Firebase init check: sa_json_env={'SET' if sa_json_env else 'NOT SET'}, "
                     f"client_email={'SET' if client_email else 'NOT SET'}, "
                     f"private_key={'SET' if private_key else 'NOT SET'}, "
                     f"sa_path={sa_path}, sa_path_exists={sa_path and os.path.exists(sa_path)}")

        if sa_json_env:
            import json
            # Handle potential escaping issues in the JSON string
            try:
                cred_dict = json.loads(sa_json_env)
            except json.JSONDecodeError:
                # Try unescaping if it was double-escaped
                sa_json_env = sa_json_env.replace("\\\\n", "\\n")
                cred_dict = json.loads(sa_json_env)
            # Fix private_key newlines in the parsed dict
            if "private_key" in cred_dict:
                pk = cred_dict["private_key"]
                # Handle both \\n (literal backslash-n) and already-correct \n
                pk = pk.replace("\\n", "\n")
                cred_dict["private_key"] = pk
            cred = credentials.Certificate(cred_dict)
            firebase_app = firebase_admin.initialize_app(cred)
            is_firebase_initialized = True
            logger.info("Firebase Admin initialized with FIREBASE_SERVICE_ACCOUNT_JSON environment variable.")
        elif client_email and private_key:
            # Handle multiple levels of escaping that can happen with env vars
            # Render may store the key with literal \n, \\n, or actual newlines
            formatted_pk = private_key
            if "\\\\n" in formatted_pk:
                formatted_pk = formatted_pk.replace("\\\\n", "\n")
            elif "\\n" in formatted_pk:
                formatted_pk = formatted_pk.replace("\\n", "\n")
            # Strip surrounding quotes if present
            formatted_pk = formatted_pk.strip().strip("'\"")
            cred_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key": formatted_pk,
                "client_email": client_email,
            }
            cred = credentials.Certificate(cred_dict)
            firebase_app = firebase_admin.initialize_app(cred)
            is_firebase_initialized = True
            logger.info("Firebase Admin initialized with client_email and private_key environment variables.")
        elif sa_path and os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)
            firebase_app = firebase_admin.initialize_app(cred)
            is_firebase_initialized = True
            logger.info("Firebase Admin initialized with service account certificate file.")
        else:
            # Fallback initialization using project ID
            firebase_app = firebase_admin.initialize_app(
                options={"projectId": settings.FIREBASE_PROJECT_ID}
            )
            is_firebase_initialized = True
            logger.warning(
                f"Firebase Admin initialized using projectId={settings.FIREBASE_PROJECT_ID} "
                "without service account credentials. Firebase Auth operations will fail unless credentials are provided via environment variables."
            )
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}", exc_info=True)
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

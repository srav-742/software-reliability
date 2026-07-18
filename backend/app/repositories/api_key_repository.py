import hashlib
import secrets
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.api_key import ApiKey
from app.models.user import User


class ApiKeyRepository:
    @staticmethod
    def hash_key(raw_key: str) -> str:
        """Hash an API key using SHA-256."""
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def generate_api_key(self, prefix: str = "sra_") -> Tuple[str, str, str]:
        """
        Generate a new random API key.
        Returns (raw_key, key_prefix, key_hash).
        """
        random_part = secrets.token_hex(20)
        raw_key = f"{prefix}{random_part}"
        key_prefix = raw_key[:10]  # e.g., 'sra_a1b2c3'
        key_hash = self.hash_key(raw_key)
        return raw_key, key_prefix, key_hash

    def create(self, db: Session, user_id: int, name: str) -> Tuple[ApiKey, str]:
        """Create a new API Key record and return (api_key_db_obj, raw_key_str)."""
        raw_key, key_prefix, key_hash = self.generate_api_key()
        api_key_obj = ApiKey(
            user_id=user_id,
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            is_active=True,
        )
        db.add(api_key_obj)
        db.commit()
        db.refresh(api_key_obj)
        return api_key_obj, raw_key

    def get_user_keys(self, db: Session, user_id: int) -> List[ApiKey]:
        """List all active API keys for a user."""
        return db.query(ApiKey).filter(ApiKey.user_id == user_id, ApiKey.is_active == True).all()

    def validate_key(self, db: Session, raw_key: str) -> Optional[User]:
        """
        Validate raw API key against database.
        Returns associated active User if valid, else None.
        """
        if not raw_key:
            return None

        key_hash = self.hash_key(raw_key.strip())
        api_key_obj = db.query(ApiKey).filter(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True
        ).first()

        if not api_key_obj:
            return None

        # Update last_used_at timestamp
        api_key_obj.last_used_at = datetime.now(timezone.utc)
        db.commit()

        return api_key_obj.owner

    def revoke(self, db: Session, user_id: int, key_id: int) -> bool:
        """Deactivate an API key."""
        api_key_obj = db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == user_id
        ).first()

        if not api_key_obj:
            return False

        api_key_obj.is_active = False
        db.commit()
        return True


api_key_repository = ApiKeyRepository()

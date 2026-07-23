"""
Repository for API Key Scan database operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.api_key_scan import ApiKeyScan, DetectedApiKey


class ApiKeyScanRepository:
    """CRUD operations for ApiKeyScan and DetectedApiKey models."""

    def create_scan(
        self,
        db: Session,
        project_id: int,
        total_keys_found: int = 0,
        valid_keys: int = 0,
        invalid_keys: int = 0,
        unknown_keys: int = 0,
        scan_status: str = "completed",
    ) -> ApiKeyScan:
        """Create a new scan record."""
        scan = ApiKeyScan(
            project_id=project_id,
            total_keys_found=total_keys_found,
            valid_keys=valid_keys,
            invalid_keys=invalid_keys,
            unknown_keys=unknown_keys,
            scan_status=scan_status,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan

    def add_detected_key(
        self,
        db: Session,
        scan_id: int,
        provider: str,
        key_masked: str,
        file_path: str,
        line_number: int,
        status: str,
        error_message: Optional[str] = None,
        failure_chance: float = 0.0,
        risk_level: str = "low",
    ) -> DetectedApiKey:
        """Add a detected key to a scan."""
        detected = DetectedApiKey(
            scan_id=scan_id,
            provider=provider,
            key_masked=key_masked,
            file_path=file_path,
            line_number=line_number,
            status=status,
            error_message=error_message,
            failure_chance=failure_chance,
            risk_level=risk_level,
        )
        db.add(detected)
        db.commit()
        db.refresh(detected)
        return detected

    def add_detected_keys_bulk(
        self,
        db: Session,
        scan_id: int,
        keys_data: list,
    ) -> None:
        """Add multiple detected keys at once."""
        for key_data in keys_data:
            detected = DetectedApiKey(
                scan_id=scan_id,
                provider=key_data["provider"],
                key_masked=key_data["key_masked"],
                file_path=key_data["file_path"],
                line_number=key_data["line_number"],
                status=key_data["status"],
                error_message=key_data.get("error_message"),
                failure_chance=key_data.get("failure_chance", 0.0),
                risk_level=key_data.get("risk_level", "low"),
            )
            db.add(detected)
        db.commit()

    def get_latest_scan(self, db: Session, project_id: int) -> Optional[ApiKeyScan]:
        """Get the most recent scan for a project."""
        return (
            db.query(ApiKeyScan)
            .filter(ApiKeyScan.project_id == project_id)
            .order_by(ApiKeyScan.scanned_at.desc())
            .first()
        )

    def get_scan_by_id(self, db: Session, scan_id: int) -> Optional[ApiKeyScan]:
        """Get a specific scan by its ID."""
        return db.query(ApiKeyScan).filter(ApiKeyScan.id == scan_id).first()

    def get_scan_history(
        self,
        db: Session,
        project_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ApiKeyScan]:
        """Get all scans for a project, ordered by most recent first."""
        return (
            db.query(ApiKeyScan)
            .filter(ApiKeyScan.project_id == project_id)
            .order_by(ApiKeyScan.scanned_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_scans_for_project(self, db: Session, project_id: int) -> int:
        """Delete all scans for a project. Returns count of deleted scans."""
        count = (
            db.query(ApiKeyScan)
            .filter(ApiKeyScan.project_id == project_id)
            .delete(synchronize_session="fetch")
        )
        db.commit()
        return count


api_key_scan_repository = ApiKeyScanRepository()

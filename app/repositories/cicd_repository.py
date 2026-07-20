from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.cicd_scan import CICDScan


class CICDRepository:
    def create(
        self,
        db: Session,
        project_id: int,
        user_id: int,
        risk_score: float,
        failure_probability: float,
        status: str,
        commit_sha: Optional[str] = None,
        branch: Optional[str] = None,
        author: Optional[str] = None,
        pass_threshold: float = 50.0,
        warn_threshold: float = 80.0,
        metrics_summary: Optional[dict] = None,
        report_markdown: Optional[str] = None,
    ) -> CICDScan:
        scan = CICDScan(
            project_id=project_id,
            user_id=user_id,
            commit_sha=commit_sha,
            branch=branch,
            author=author,
            risk_score=risk_score,
            failure_probability=failure_probability,
            status=status,
            pass_threshold=pass_threshold,
            warn_threshold=warn_threshold,
            metrics_summary=metrics_summary,
            report_markdown=report_markdown,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan

    def get_by_id(self, db: Session, scan_id: int) -> Optional[CICDScan]:
        return db.query(CICDScan).filter(CICDScan.id == scan_id).first()

    def get_user_scans(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[CICDScan]:
        return (
            db.query(CICDScan)
            .order_by(CICDScan.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_project_scans(self, db: Session, project_id: int, skip: int = 0, limit: int = 50) -> List[CICDScan]:
        return (
            db.query(CICDScan)
            .filter(CICDScan.project_id == project_id)
            .order_by(CICDScan.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


cicd_repository = CICDRepository()

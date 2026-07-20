import os
from typing import Any, Dict, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.feature_extraction.extractor import FeatureExtractor
from app.models.user import User
from app.models.project import Project
from app.repositories.project_repository import project_repository
from app.repositories.metrics_repository import metrics_repository
from app.repositories.cicd_repository import cicd_repository
from app.schemas.project import ProjectCreate
from app.schemas.metrics import MetricCreate
from app.services.project_service import project_service
from app.services.prediction_service import prediction_service
from app.ml.inference.model_loader import is_model_available


class CICDService:
    def process_scan(
        self,
        db: Session,
        user: User,
        source_code_file: UploadFile,
        project_id: Optional[int] = None,
        project_name: Optional[str] = None,
        commit_sha: Optional[str] = None,
        branch: Optional[str] = None,
        author: Optional[str] = None,
        pass_threshold: float = 50.0,
        warn_threshold: float = 80.0,
    ) -> Dict[str, Any]:
        """
        Execute an automated atomic CI/CD scan for uploaded source code.
        """

        # 1. Resolve or create project
        project = None
        if project_id:
            project = project_repository.get(db, id=project_id)
            if not project or project.user_id != user.id:
                raise ValueError(f"Project with ID {project_id} not found or access denied.")
        elif project_name:
            # Find project by name for this user or create if absent
            existing = (
                db.query(Project)
                .filter(Project.user_id == user.id, Project.project_name == project_name)
                .first()
            )
            if existing:
                project = existing
            else:
                project = project_repository.create(
                    db,
                    obj_in=ProjectCreate(
                        project_name=project_name,
                        language="Python",
                        description=f"Automated CI/CD project for {project_name}",
                    ),
                    user_id=user.id,
                )
        else:
            # Default fallback project name
            project_name_fallback = f"CI Build {commit_sha[:7] if commit_sha else 'Scan'}"
            project = project_repository.create(
                db,
                obj_in=ProjectCreate(
                    project_name=project_name_fallback,
                    language="Python",
                    description="Automated CI/CD build scan",
                ),
                user_id=user.id,
            )

        # 2. Save source code zip file
        saved_path = project_service.save_source_code(source_code_file)
        project.source_code_path = saved_path
        db.commit()

        # 3. Feature Extraction
        extracted_features = FeatureExtractor.extract_from_path(saved_path)

        # Save metrics record
        metric_in = MetricCreate(project_id=project.id, **extracted_features)
        saved_metric = metrics_repository.create(db, obj_in=metric_in)

        # 4. ML Prediction
        if not is_model_available():
            raise ValueError(
                "No trained ML model available on the server. Please train a model via POST /api/v1/train first."
            )

        pred_result = prediction_service.predict_project(db=db, project_id=project.id)

        failure_prob = pred_result["failure_probability"]
        risk_score = round(failure_prob * 100.0, 2)

        # 5. Evaluate Policy Thresholds
        # Policy:
        # risk_score >= warn_threshold (e.g. 80.0%) -> FAIL
        # risk_score >= pass_threshold (e.g. 50.0%) -> WARN
        # risk_score < pass_threshold -> PASS
        if risk_score >= warn_threshold:
            status = "FAIL"
            exit_code = 1
        elif risk_score >= pass_threshold:
            status = "WARN"
            exit_code = 0
        else:
            status = "PASS"
            exit_code = 0

        # 6. Generate GitHub Markdown Report Summary
        report_md = self._generate_markdown_report(
            project_name=project.project_name,
            commit_sha=commit_sha,
            branch=branch,
            author=author,
            status=status,
            risk_score=risk_score,
            failure_prob=failure_prob,
            rel_stats=pred_result.get("reliability_stats", {}),
            extracted_features=extracted_features,
            recommendations=pred_result.get("recommendations", []),
            pass_threshold=pass_threshold,
            warn_threshold=warn_threshold,
        )

        # 7. Persist Scan Record
        scan_record = cicd_repository.create(
            db=db,
            project_id=project.id,
            user_id=user.id,
            commit_sha=commit_sha,
            branch=branch,
            author=author,
            risk_score=risk_score,
            failure_probability=failure_prob,
            status=status,
            pass_threshold=pass_threshold,
            warn_threshold=warn_threshold,
            metrics_summary=extracted_features,
            report_markdown=report_md,
        )

        return {
            "scan_id": scan_record.id,
            "project_id": project.id,
            "project_name": project.project_name,
            "commit_sha": commit_sha,
            "branch": branch,
            "status": status,
            "exit_code": exit_code,
            "risk_score": risk_score,
            "failure_probability": failure_prob,
            "pass_threshold": pass_threshold,
            "warn_threshold": warn_threshold,
            "reliability_stats": pred_result.get("reliability_stats"),
            "recommendations": pred_result.get("recommendations", []),
            "report_markdown": report_md,
        }

    def _generate_markdown_report(
        self,
        project_name: str,
        commit_sha: Optional[str],
        branch: Optional[str],
        author: Optional[str],
        status: str,
        risk_score: float,
        failure_prob: float,
        rel_stats: dict,
        extracted_features: dict,
        recommendations: list,
        pass_threshold: float,
        warn_threshold: float,
    ) -> str:
        status_badge = "🟢 **PASS**" if status == "PASS" else ("🟡 **WARN**" if status == "WARN" else "🔴 **FAIL**")
        commit_str = commit_sha[:7] if commit_sha else "N/A"
        branch_str = branch if branch else "N/A"
        mtbf_val = rel_stats.get("mtbf", "N/A")

        recs_md = ""
        if recommendations:
            for rec in recommendations[:3]:
                if isinstance(rec, dict):
                    recs_md += f"- **[{rec.get('severity', 'HIGH')}]** {rec.get('issue', '')} — *{rec.get('action', '')}*\n"
                else:
                    recs_md += f"- {rec}\n"
        else:
            recs_md = "_No critical refactoring actions required._\n"

        lines_code = extracted_features.get("lines_of_code", 0)
        cyclomatic = extracted_features.get("cyclomatic_complexity", 0)
        maint_idx = extracted_features.get("maintainability_index", 0)

        md = f"""# 🛡️ Software Reliability Report

### Build Assessment: {status_badge}

| Metric | Score / Value | Target Policy |
| :--- | :--- | :--- |
| **Risk Score** | **{risk_score}%** | Pass < {pass_threshold}% | Fail > {warn_threshold}% |
| **Failure Probability** | `{failure_prob:.4f}` | Low Risk < 0.50 |
| **Est. MTBF** | `{mtbf_val} hours` | Operational Stability |
| **Lines of Code** | `{lines_code}` | Codebase Volume |
| **Cyclomatic Complexity** | `{cyclomatic:.1f}` | Lower is safer (< 20) |
| **Maintainability Index** | `{maint_idx:.1f}` | Higher is better (> 65) |

**Build Details:**
- **Project:** `{project_name}`
- **Commit:** `{commit_str}`
- **Branch:** `{branch_str}`
- **Author:** `{author or 'Unknown'}`

### 🚨 Refactoring Recommendations
{recs_md}
---
*Report generated by Software Reliability AI Platform*
"""
        return md


cicd_service = CICDService()

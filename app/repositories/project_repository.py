from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def get(self, db: Session, id: int) -> Optional[Project]:
        return db.get(Project, id)

    def get_by_user(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        return (
            db.query(Project)
            .filter(Project.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self, db: Session, *, obj_in: ProjectCreate, user_id: int, source_code_path: Optional[str] = None
    ) -> Project:
        db_obj = Project(
            user_id=user_id,
            project_name=obj_in.project_name,
            repository_url=obj_in.repository_url,
            source_code_path=source_code_path,
            language=obj_in.language,
            framework=obj_in.framework,
            description=obj_in.description,
            status="Uploaded"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Project, obj_in: ProjectUpdate, source_code_path: Optional[str] = None
    ) -> Project:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        if source_code_path is not None:
            db_obj.source_code_path = source_code_path
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[Project]:
        obj = db.get(Project, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


project_repository = ProjectRepository()

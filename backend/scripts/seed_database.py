import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.metrics import ApiMetric
from app.core.security import get_password_hash
from app.ml.datasets.generate_dataset import generate_synthetic_dataset

def seed():
    db = SessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == "testuser@example.com").first()
        if not user:
            user = User(
                full_name="Test User",
                email="testuser@example.com",
                password_hash=get_password_hash("password"),
                role="developer",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user: {user.email}")
        else:
            print(f"User {user.email} already exists.")

        # Check if project already exists
        project = db.query(Project).filter(Project.project_name == "Test Software Project").first()
        if not project:
            project = Project(
                user_id=user.id,
                project_name="Test Software Project",
                repository_url="https://github.com/example/test-software-project",
                language="Python",
                description="Seeded project for testing software reliability model",
                status="Analyzed"
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            print(f"Created project: {project.project_name}")
        else:
            print(f"Project {project.project_name} already exists.")

        # Seed metrics if none exist
        metrics_count = db.query(ApiMetric).filter(ApiMetric.project_id == project.id).count()
        if metrics_count == 0:
            print("Generating synthetic metrics...")
            df = generate_synthetic_dataset(n_samples=100, seed=42)
            for _, row in df.iterrows():
                metric = ApiMetric(
                    project_id=project.id,
                    lines_of_code=int(row["lines_of_code"]),
                    cyclomatic_complexity=int(row["cyclomatic_complexity"]),
                    number_of_functions=int(row["number_of_functions"]),
                    number_of_parameters=int(row["number_of_parameters"]),
                    nested_depth=int(row["nested_depth"]),
                    if_statement_count=int(row["if_statement_count"]),
                    loop_count=int(row["loop_count"]),
                    imports_count=int(row["imports_count"]),
                    dependency_count=int(row["dependency_count"]),
                    duplicate_code_score=float(row["duplicate_code_score"]),
                    exception_handling_count=int(row["exception_handling_count"]),
                    database_queries=int(row["database_queries"]),
                    external_api_calls=int(row["external_api_calls"]),
                    cpu_usage=float(row["cpu_usage"]),
                    memory_usage=float(row["memory_usage"]),
                    average_response_time=float(row["average_response_time"]),
                    test_coverage=float(row["test_coverage"]),
                    historical_bug_count=int(row["historical_bug_count"]),
                    api_failure=int(row["api_failure"])
                )
                db.add(metric)
            db.commit()
            print("Successfully seeded 100 API metric records.")
        else:
            print(f"API Metrics ({metrics_count} records) already exist for this project.")

    finally:
        db.close()

if __name__ == "__main__":
    seed()

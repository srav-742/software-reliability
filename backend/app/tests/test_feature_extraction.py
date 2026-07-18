import sys
import os
import uuid
import io
import zipfile

# Add backend root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.feature_extraction.parser import analyze_python_file
from app.feature_extraction.extractor import FeatureExtractor

client = TestClient(app)


def test_ast_python_parser():
    sample_code = """
import os
import requests

def sample_function(a, b, c=10):
    if a > b:
        for i in range(5):
            print(i)
    try:
        res = requests.get("https://api.example.com")
        db.query(User).filter(User.id == a).first()
    except Exception as e:
        print(e)
    return a + b
"""
    result = analyze_python_file(sample_code)

    assert result["lines_of_code"] > 5
    assert result["cyclomatic_complexity"] >= 4
    assert result["number_of_functions"] == 1
    assert result["number_of_parameters"] == 3
    assert result["if_statement_count"] == 1
    assert result["loop_count"] == 1
    assert result["imports_count"] == 2
    assert result["exception_handling_count"] == 1
    assert result["database_queries"] >= 1
    assert result["external_api_calls"] >= 1


def test_feature_extraction_api_flow():
    db = SessionLocal()
    unique_suffix = uuid.uuid4().hex[:8]
    user_email = f"extract_user_{unique_suffix}@example.com"
    password = "SecurePassword123!"

    user_id = None
    try:
        # 1. Register User
        reg_payload = {
            "email": user_email,
            "password": password,
            "full_name": f"Extract User {unique_suffix}",
            "role": "developer"
        }
        res_reg = client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        user_id = res_reg.json()["id"]

        # 2. Login User
        res_login = client.post("/api/v1/auth/login", json={"email": user_email, "password": password})
        assert res_login.status_code == 200
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create Project with mock uploaded Python zip archive
        mock_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(mock_zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "main.py",
                """
import requests

def calc(x, y):
    if x > 10:
        return x * y
    return x + y
"""
            )
            zip_file.writestr("requirements.txt", "requests==2.28.1\nfastapi==0.95.0\n")

        mock_zip_buffer.seek(0)
        proj_data = {
            "project_name": f"Analysis Proj {unique_suffix}",
            "language": "Python",
            "framework": "FastAPI"
        }
        files = {"source_code_file": ("source.zip", mock_zip_buffer, "application/zip")}

        res_proj = client.post("/api/v1/projects/", data=proj_data, files=files, headers=headers)
        assert res_proj.status_code == 201, res_proj.text
        proj_id = res_proj.json()["id"]

        # 4. Trigger Analysis / Feature Extraction
        res_analyze = client.post(f"/api/v1/projects/{proj_id}/analyze", headers=headers)
        assert res_analyze.status_code == 201, res_analyze.text
        metrics = res_analyze.json()

        assert metrics["project_id"] == proj_id
        assert metrics["lines_of_code"] >= 5
        assert metrics["dependency_count"] == 2
        assert metrics["number_of_functions"] >= 1
        assert "cyclomatic_complexity" in metrics

        # 5. Fetch Metrics via GET endpoint
        res_get_metrics = client.get(f"/api/v1/projects/{proj_id}/metrics", headers=headers)
        assert res_get_metrics.status_code == 200
        assert res_get_metrics.json()["id"] == metrics["id"]

        # Cleanup Project
        client.delete(f"/api/v1/projects/{proj_id}", headers=headers)

    finally:
        if user_id:
            u = db.query(User).filter(User.id == user_id).first()
            if u:
                db.delete(u)
                db.commit()
        db.close()


if __name__ == "__main__":
    test_ast_python_parser()
    test_feature_extraction_api_flow()

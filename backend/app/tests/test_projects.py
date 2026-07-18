import sys
import os
import uuid
import io

# Add the backend root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.models.project import Project

client = TestClient(app)


def test_project_management_flow():
    db = SessionLocal()

    # Generate unique test data for User
    unique_suffix = uuid.uuid4().hex[:8]
    user1_email = f"user1_{unique_suffix}@example.com"
    user2_email = f"user2_{unique_suffix}@example.com"
    password = "SecurePassword123!"

    user1_id = None
    user2_id = None

    try:
        # Register User 1
        reg_payload1 = {
            "email": user1_email,
            "password": password,
            "full_name": f"User One {unique_suffix}",
            "role": "developer"
        }
        res1 = client.post("/api/v1/auth/register", json=reg_payload1)
        assert res1.status_code == 201, f"Registration of user1 failed: {res1.text}"
        user1_id = res1.json()["id"]

        # Register User 2
        reg_payload2 = {
            "email": user2_email,
            "password": password,
            "full_name": f"User Two {unique_suffix}",
            "role": "developer"
        }
        res2 = client.post("/api/v1/auth/register", json=reg_payload2)
        assert res2.status_code == 201, f"Registration of user2 failed: {res2.text}"
        user2_id = res2.json()["id"]

        # Log in User 1
        login_res1 = client.post("/api/v1/auth/login", json={"email": user1_email, "password": password})
        assert login_res1.status_code == 200
        token1 = login_res1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Log in User 2
        login_res2 = client.post("/api/v1/auth/login", json={"email": user2_email, "password": password})
        assert login_res2.status_code == 200
        token2 = login_res2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # -------------------------------------------------------------
        # 1. Create project with metadata only
        # -------------------------------------------------------------
        print("\n[STEP 1] Creating project with metadata only...")
        proj_data_1 = {
            "project_name": "Metadata Project",
            "language": "Python",
            "framework": "FastAPI",
            "repository_url": "https://github.com/example/metadata-proj",
            "description": "Test project with no file upload"
        }
        # Note: /projects/ expects multipart Form data
        response = client.post("/api/v1/projects/", data=proj_data_1, headers=headers1)
        assert response.status_code == 201, response.text
        proj1_id = response.json()["id"]
        assert response.json()["project_name"] == "Metadata Project"
        assert response.json()["source_code_path"] is None
        print("[SUCCESS] Metadata project created.")

        # -------------------------------------------------------------
        # 2. Create project with metadata AND source code upload
        # -------------------------------------------------------------
        print("\n[STEP 2] Creating project with file upload...")
        proj_data_2 = {
            "project_name": "Upload Project",
            "language": "JavaScript",
            "framework": "Next.js",
            "repository_url": "https://github.com/example/upload-proj",
            "description": "Test project with mock zip file upload"
        }
        mock_file = io.BytesIO(b"fake zip archive content")
        files = {"source_code_file": ("code.zip", mock_file, "application/zip")}

        response = client.post("/api/v1/projects/", data=proj_data_2, files=files, headers=headers1)
        assert response.status_code == 201, response.text
        proj2_data = response.json()
        proj2_id = proj2_data["id"]
        assert proj2_data["project_name"] == "Upload Project"
        assert proj2_data["source_code_path"] is not None
        assert proj2_data["source_code_path"].endswith("code.zip")
        # Keep path to verify disk deletion later
        saved_file_path = proj2_data["source_code_path"]
        print(f"[SUCCESS] Upload project created with path: {saved_file_path}")

        # -------------------------------------------------------------
        # 3. Retrieve list of projects for User 1
        # -------------------------------------------------------------
        print("\n[STEP 3] Fetching projects list for User 1...")
        response = client.get("/api/v1/projects/", headers=headers1)
        assert response.status_code == 200
        projects_list = response.json()
        assert len(projects_list) >= 2
        project_ids = [p["id"] for p in projects_list]
        assert proj1_id in project_ids
        assert proj2_id in project_ids
        print("[SUCCESS] Projects list retrieved successfully.")

        # -------------------------------------------------------------
        # 4. Fetch detailed project view
        # -------------------------------------------------------------
        print("\n[STEP 4] Fetching detailed project view...")
        response = client.get(f"/api/v1/projects/{proj1_id}", headers=headers1)
        assert response.status_code == 200
        assert response.json()["project_name"] == "Metadata Project"
        print("[SUCCESS] Detailed view matches.")

        # -------------------------------------------------------------
        # 5. Access control verification (User 2 should NOT see User 1's project)
        # -------------------------------------------------------------
        print("\n[STEP 5] Testing access control...")
        response = client.get(f"/api/v1/projects/{proj1_id}", headers=headers2)
        assert response.status_code == 404
        print("[SUCCESS] Unauthorized access blocked successfully.")

        # -------------------------------------------------------------
        # 6. Update project (metadata & upload new file)
        # -------------------------------------------------------------
        print("\n[STEP 6] Updating project metadata and uploading new file...")
        update_data = {
            "project_name": "Updated Upload Project",
            "framework": "React"
        }
        mock_file_updated = io.BytesIO(b"updated fake zip archive content")
        files_updated = {"source_code_file": ("new_code.zip", mock_file_updated, "application/zip")}

        response = client.put(f"/api/v1/projects/{proj2_id}", data=update_data, files=files_updated, headers=headers1)
        assert response.status_code == 200
        updated_proj2 = response.json()
        assert updated_proj2["project_name"] == "Updated Upload Project"
        assert updated_proj2["framework"] == "React"
        # Source code path should be updated and old one cleaned up
        new_file_path = updated_proj2["source_code_path"]
        assert new_file_path is not None
        assert new_file_path.endswith("new_code.zip")
        assert new_file_path != saved_file_path

        # Verify old file was deleted from disk
        assert not os.path.exists(saved_file_path), "Old uploaded file was not cleaned up!"
        assert os.path.exists(new_file_path), "New file was not saved!"
        print(f"[SUCCESS] Project updated and file rollover succeeded. New path: {new_file_path}")

        # -------------------------------------------------------------
        # 7. Delete project
        # -------------------------------------------------------------
        print("\n[STEP 7] Deleting project...")
        response = client.delete(f"/api/v1/projects/{proj2_id}", headers=headers1)
        assert response.status_code == 204

        # Verify project is gone
        response = client.get(f"/api/v1/projects/{proj2_id}", headers=headers1)
        assert response.status_code == 404

        # Verify new file is deleted from disk
        assert not os.path.exists(new_file_path), "Source code file was not deleted from disk!"
        print("[SUCCESS] Project deleted from database and disk cleanup verified.")

        # Clean up metadata project
        client.delete(f"/api/v1/projects/{proj1_id}", headers=headers1)

    finally:
        db_cleanup = SessionLocal()
        try:
            print("\n[CLEANUP] Cleaning up test users and remaining projects...")
            # Clean up users (projects are cascading deletion)
            if user1_id:
                u1 = db_cleanup.query(User).filter(User.id == user1_id).first()
                if u1:
                    db_cleanup.delete(u1)
            if user2_id:
                u2 = db_cleanup.query(User).filter(User.id == user2_id).first()
                if u2:
                    db_cleanup.delete(u2)
            db_cleanup.commit()
            print("[CLEANUP] Done.")
        except Exception as e:
            print(f"[WARNING] Database cleanup failed: {e}")
        finally:
            db_cleanup.close()
            db.close()


if __name__ == "__main__":
    test_project_management_flow()

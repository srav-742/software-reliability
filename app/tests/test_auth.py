import sys
import os
import uuid

# Add the backend root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User

client = TestClient(app)


def test_authentication_flow():
    db = SessionLocal()
    
    # Generate unique test data
    unique_suffix = uuid.uuid4().hex[:8]
    test_email = f"test_auth_{unique_suffix}@example.com"
    test_password = "SecurePassword123!"
    test_name = f"Test Auth User {unique_suffix}"
    
    print(f"\n[INFO] Starting integration test for user email: {test_email}")
    
    try:
        # 1. Register User
        print("[STEP 1] Registering test user...")
        reg_payload = {
            "email": test_email,
            "password": test_password,
            "full_name": test_name,
            "role": "developer"
        }
        response = client.post("/api/v1/auth/register", json=reg_payload)
        assert response.status_code == 201, f"Registration failed: {response.text}"
        data = response.json()
        assert data["email"] == test_email
        assert data["full_name"] == test_name
        assert "password_hash" not in data, "Security error: password hash returned in response!"
        print("[SUCCESS] Registration successful.")
        
        # 1b. Duplicate Registration (Should fail)
        print("[STEP 1B] Verifying duplicate registration protection...")
        response_dup = client.post("/api/v1/auth/register", json=reg_payload)
        assert response_dup.status_code == 400, "Error: Allowed registering user with duplicate email!"
        print("[SUCCESS] Duplicate registration rejected correctly.")

        # 2. Login User
        print("[STEP 2] Verifying login endpoint...")
        login_payload = {
            "email": test_email,
            "password": test_password
        }
        response = client.post("/api/v1/auth/login", json=login_payload)
        assert response.status_code == 200, f"Login failed: {response.text}"
        login_data = response.json()
        assert "access_token" in login_data, "Error: access_token not found in response!"
        assert login_data["token_type"] == "bearer", "Error: token_type is not bearer!"
        
        access_token = login_data["access_token"]
        
        # Verify Firebase token presence/status
        firebase_token = login_data.get("firebase_token")
        if firebase_token:
            print(f"[INFO] Firebase Custom Token successfully generated: {firebase_token[:15]}...")
        else:
            print("[INFO] Firebase token is None (expected fallback if service account is not configured).")
            
        print("[SUCCESS] Login successful, access token retrieved.")
        
        # 2b. Incorrect Login (Should fail)
        print("[STEP 2B] Verifying login with wrong password...")
        bad_login_payload = {
            "email": test_email,
            "password": "WrongPasswordValue"
        }
        response_bad = client.post("/api/v1/auth/login", json=bad_login_payload)
        assert response_bad.status_code == 401, "Error: Logged in successfully with bad credentials!"
        print("[SUCCESS] Bad credentials login rejected correctly.")

        # 3. Retrieve Profile (Protected Route)
        print("[STEP 3] Verifying access to protected /auth/profile endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200, f"Failed to get profile: {response.text}"
        profile_data = response.json()
        assert profile_data["email"] == test_email
        assert profile_data["full_name"] == test_name
        print("[SUCCESS] Profile details retrieved and matched.")
        
        # 3b. Access Profile without token (Should fail)
        print("[STEP 3B] Verifying access to protected endpoint without auth header...")
        response_no_header = client.get("/api/v1/auth/profile")
        assert response_no_header.status_code == 401, "Error: Accessed protected profile without token!"
        print("[SUCCESS] Unauthorized request blocked correctly.")
        
        print("\n[COMPLETE] --- ALL INTEGRATION TESTS PASSED SUCCESSFULLY! ---")
        
    finally:
        # Cleanup
        print("[CLEANUP] Removing test user from local database...")
        db_cleanup = SessionLocal()
        try:
            test_user = db_cleanup.query(User).filter(User.email == test_email).first()
            if test_user:
                db_cleanup.delete(test_user)
                db_cleanup.commit()
                print("[CLEANUP] Database records cleaned up successfully.")
        except Exception as e:
            print(f"[WARNING] Database cleanup failed: {e}")
        finally:
            db_cleanup.close()
            db.close()


if __name__ == "__main__":
    test_authentication_flow()

import sys
import os
import uuid

# Add backend root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_training_endpoints():
    # 1. Register a test user
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"trainer_{unique_suffix}@example.com"
    password = "SecurePassword123!"
    
    reg_payload = {
        "email": email,
        "password": password,
        "full_name": f"Trainer {unique_suffix}",
        "role": "developer"
    }
    
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
    
    # 2. Login the test user
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Call POST /api/v1/train to train a simple model
    # We restrict algorithms to 'logistic_regression' for speed in tests
    train_payload = {
        "algorithms": ["logistic_regression"],
        "test_size": 0.2
    }
    train_res = client.post("/api/v1/train", json=train_payload, headers=headers)
    assert train_res.status_code == 201, f"Training failed: {train_res.text}"
    
    res_data = train_res.json()
    assert res_data["status"] == "success"
    assert res_data["best_algorithm"] == "logistic_regression"
    assert len(res_data["all_results"]) == 1
    assert "model_path" in res_data["model_paths"]
    
    # 4. Call GET /api/v1/train/history to retrieve training history
    history_res = client.get("/api/v1/train/history", headers=headers)
    assert history_res.status_code == 200, f"Fetching history failed: {history_res.text}"
    history_data = history_res.json()
    assert len(history_data) >= 1
    assert history_data[0]["algorithm"] == "logistic_regression"

import sys
import os
import uuid

# Add backend root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_prediction_endpoints():
    # 1. Register a test user
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"predictor_{unique_suffix}@example.com"
    password = "SecurePassword123!"
    
    reg_payload = {
        "email": email,
        "password": password,
        "full_name": f"Predictor {unique_suffix}",
        "role": "developer"
    }
    
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    
    # 2. Login the test user
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Train a model so that is_model_available() returns True
    train_payload = {
        "algorithms": ["logistic_regression"],
        "test_size": 0.2
    }
    train_res = client.post("/api/v1/train", json=train_payload, headers=headers)
    assert train_res.status_code == 201
    
    # 4. Create a project
    proj_payload = {
        "project_name": f"Predict Project {unique_suffix}",
        "language": "Python",
        "framework": "FastAPI",
        "repository_url": "https://github.com/example/pred-proj",
        "description": "Test project for reliability prediction"
    }
    proj_res = client.post("/api/v1/projects/", data=proj_payload, headers=headers)
    assert proj_res.status_code == 201, proj_res.text
    project_id = proj_res.json()["id"]
    
    # 5. Analyze the project to extract metrics
    analyze_res = client.post(f"/api/v1/projects/{project_id}/analyze", headers=headers)
    assert analyze_res.status_code == 201, analyze_res.text
    
    # 6. Call prediction endpoint
    predict_res = client.post(f"/api/v1/projects/{project_id}/predict", headers=headers)
    assert predict_res.status_code == 201, predict_res.text
    
    pred_data = predict_res.json()
    assert pred_data["project_id"] == project_id
    assert "failure_probability" in pred_data
    assert "risk_level" in pred_data
    assert "reliability_stats" in pred_data
    
    # 7. Get prediction history
    history_res = client.get(f"/api/v1/projects/{project_id}/predictions", headers=headers)
    assert history_res.status_code == 200, history_res.text
    history_data = history_res.json()
    assert len(history_data) >= 1
    assert history_data[0]["project_id"] == project_id

    # 8. Get prediction explanation (SHAP values)
    explain_res = client.get(f"/api/v1/projects/{project_id}/explain", headers=headers)
    assert explain_res.status_code == 200, explain_res.text
    explain_data = explain_res.json()
    assert explain_data["project_id"] == project_id
    assert "shap_values" in explain_data
    assert "top_risk_factors" in explain_data

import sys
import os
import numpy as np

# Ensure backend root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.training.random_forest import create_random_forest
from app.ml.training.xgboost_model import create_xgboost
from app.ml.training.lightgbm_model import create_lightgbm
from app.ml.training.catboost_model import create_catboost
from app.ml.training.svm import create_svm
from app.ml.training.decision_tree import create_decision_tree
from app.ml.training.logistic import create_logistic_regression
from app.ml.training.trainer import create_voting_ensemble

def run_model_verification():
    print("=== Starting ML Model Verification ===")
    
    # Generate dummy binary classification data
    X = np.random.rand(50, 10)
    y = np.random.randint(0, 2, 50)
    
    models = {
        "Voting Ensemble": create_voting_ensemble(),
        "Random Forest": create_random_forest(),
        "XGBoost": create_xgboost(),
        "LightGBM": create_lightgbm(),
        "CatBoost": create_catboost(iterations=10),  # low iterations for speed
        "SVM": create_svm(),
        "Decision Tree": create_decision_tree(),
        "Logistic Regression": create_logistic_regression(),
    }
    
    all_success = True
    for name, model in models.items():
        try:
            print(f"Testing {name}...")
            model.fit(X, y)
            preds = model.predict(X)
            print(f"  [SUCCESS] {name} trained and predicted successfully. Shape of predictions: {preds.shape}")
        except Exception as e:
            print(f"  [FAILED] {name} failed with error: {str(e)}")
            all_success = False
            
    if all_success:
        print("\n=== ALL MODELS VERIFIED SUCCESSFULLY ===")
        sys.exit(0)
    else:
        print("\n=== SOME MODELS FAILED VERIFICATION ===")
        sys.exit(1)

if __name__ == "__main__":
    run_model_verification()

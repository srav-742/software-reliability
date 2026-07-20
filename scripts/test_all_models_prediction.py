import sys
import os
import pandas as pd

# Ensure backend root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.preprocessing.preprocessing_pipeline import PreprocessingPipeline
from app.ml.training.trainer import ModelTrainer

def test_predictions_all_models():
    print("=== Loading Preprocessing Pipeline ===")
    pipeline = PreprocessingPipeline()
    prep_result = pipeline.run()
    
    X_train = prep_result["X_train_scaled"]
    X_test = prep_result["X_test_scaled"]
    y_train = prep_result["y_train"]
    y_test = prep_result["y_test"]
    
    print(f"Dataset Loaded Successfully.")
    print(f"  Training samples: {X_train.shape[0]}")
    print(f"  Testing samples: {X_test.shape[0]}")
    print(f"  Number of features: {X_train.shape[1]}")
    
    print("\n=== Training & Evaluating Tuned Models (GridSearchCV) ===")
    trainer = ModelTrainer()
    train_result = trainer.train_all_models(
        X_train=X_train,
        y_train=y_train.values,
        X_test=X_test,
        y_test=y_test.values,
        tune=True
    )
    
    results = []
    for r in train_result["results"]:
        row = {
            "Model": r["algorithm"].replace("_", " ").title(),
            "Accuracy": r["metrics"]["accuracy"],
            "Precision": r["metrics"]["precision"],
            "Recall": r["metrics"]["recall"],
            "F1-Score": r["metrics"]["f1_score"],
            "ROC-AUC": r["metrics"]["roc_auc"],
            "Train Time (s)": r["training_time"]
        }
        results.append(row)
        
    df_results = pd.DataFrame(results)
    print("\n=== Evaluation Summary (Tuned Models) ===")
    print(df_results.to_string(index=False))

if __name__ == "__main__":
    test_predictions_all_models()

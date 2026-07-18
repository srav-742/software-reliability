"""
=============================================================
  COMPREHENSIVE ML MODEL TESTING SCRIPT
  Software Reliability ML Pipeline — Model Evaluation Suite
=============================================================

Checks ALL 7 models for:
  1. Accuracy / Precision / Recall / F1 / ROC-AUC
  2. Cross-Validation (5-fold Stratified)
  3. Overfitting Check  (train vs test accuracy gap)
  4. Confusion Matrix per model
  5. Model Comparison Ranking Table
  6. Saved Model (best_model.pkl) Sanity Check
  7. Feature Importance (where available)

Run from backend directory:
    python scripts/test_all_models.py
"""

import os
import sys
import json
import joblib
import warnings
import numpy as np
import pandas as pd

# ─── Path setup ───────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
warnings.filterwarnings("ignore")

# ─── Colour helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):     print(f"  {GREEN}[PASS] {msg}{RESET}")
def fail(msg):   print(f"  {RED}[FAIL] {msg}{RESET}")
def warn(msg):   print(f"  {YELLOW}[WARN] {msg}{RESET}")
def info(msg):   print(f"  {CYAN}[INFO] {msg}{RESET}")
def header(msg): print(f"\n{BOLD}{'='*60}\n  {msg}\n{'='*60}{RESET}")
def sub(msg):    print(f"\n{BOLD}  -- {msg} --{RESET}")

# ─── Imports from project ──────────────────────────────────────────────────────
from app.ml.datasets.generate_dataset import generate_synthetic_dataset
from app.ml.preprocessing.scaling import ReliabilityScaler
from app.ml.training.trainer import ModelTrainer, MODEL_REGISTRY
from app.ml.evaluation.metrics import (
    compute_classification_metrics,
    compute_reliability_statistics,
)
from app.ml.evaluation.cross_validation import perform_cross_validation
from app.ml.evaluation.comparison import compare_models

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# ─── Configuration ─────────────────────────────────────────────────────────────
N_SAMPLES     = 1200   # synthetic dataset size
TEST_SIZE     = 0.20   # 20% held-out test
RANDOM_STATE  = 42
CV_FOLDS      = 5
TUNE          = False  # Set True for hyperparameter tuning (slower)

# Thresholds for "pass"
MIN_ACCURACY  = 0.60
MIN_F1        = 0.50
MIN_ROC_AUC   = 0.60
MAX_OVERFIT   = 0.15   # max allowed (train_acc - test_acc) gap


# ======================================================================
def step1_generate_data():
    header("STEP 1 -- Generate & Prepare Dataset")
    df = generate_synthetic_dataset(n_samples=N_SAMPLES, seed=RANDOM_STATE)
    info(f"Dataset shape     : {df.shape}")
    info(f"Failure rate      : {df['api_failure'].mean()*100:.1f}%  ({df['api_failure'].sum()} failures)")
    info(f"Feature columns   : {df.shape[1]-1}")

    feature_cols = [c for c in df.columns if c != "api_failure"]
    X = df[feature_cols]
    y = df["api_failure"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    info(f"Train samples     : {len(X_train)}")
    info(f"Test samples      : {len(X_test)}")

    # Scale
    scaler = ReliabilityScaler(method="standard")
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)
    ok("Dataset generated & scaled successfully")
    return X_train_scaled, X_test_scaled, y_train.values, y_test.values, scaler, feature_cols


# ======================================================================
def step2_train_all_models(X_train, X_test, y_train, y_test):
    header("STEP 2 -- Train All 7 Models")
    trainer = ModelTrainer()
    all_algos = list(MODEL_REGISTRY.keys())
    info(f"Algorithms to train: {all_algos}")
    if not TUNE:
        warn("Hyperparameter tuning is OFF (set TUNE=True for full eval, slower)")

    output = trainer.train_all_models(
        X_train, y_train, X_test, y_test,
        algorithms=all_algos,
        tune=TUNE
    )
    results     = output["results"]
    best_result = output["best_model"]

    ok(f"Training complete. Best model: {best_result['algorithm']}")
    return results, best_result, trainer


# ======================================================================
def step3_evaluate_each_model(results, X_train, X_test, y_train, y_test):
    header("STEP 3 -- Per-Model Evaluation (Metrics + Overfitting)")
    all_pass = True
    detailed = []

    for r in results:
        algo  = r["algorithm"]
        model = r.get("model")
        sub(algo.upper())

        if model is None:
            fail(f"Model failed to train: {r.get('error', 'unknown error')}")
            all_pass = False
            continue

        metrics = r["metrics"]
        acc  = metrics["accuracy"]
        prec = metrics["precision"]
        rec  = metrics["recall"]
        f1   = metrics["f1_score"]
        auc  = metrics["roc_auc"]

        # Print metrics table
        print(f"    Accuracy  : {acc:.4f}  {'[OK]' if acc >= MIN_ACCURACY else '[LOW]'}")
        print(f"    Precision : {prec:.4f}")
        print(f"    Recall    : {rec:.4f}")
        print(f"    F1-Score  : {f1:.4f}  {'[OK]' if f1 >= MIN_F1 else '[LOW]'}")
        print(f"    ROC-AUC   : {auc:.4f}  {'[OK]' if auc >= MIN_ROC_AUC else '[LOW]'}")
        print(f"    Train time: {r['training_time']}s")

        # Overfitting check
        y_train_pred = model.predict(X_train)
        train_acc = float(np.mean(y_train_pred == y_train))
        gap = train_acc - acc
        print(f"    Train Acc : {train_acc:.4f}  (gap={gap:+.4f})")
        if gap > MAX_OVERFIT:
            warn(f"Possible overfitting! Train-Test gap = {gap:.4f}")
        else:
            ok(f"No overfitting detected (gap={gap:+.4f})")

        # Confusion Matrix
        y_pred = model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        print(f"    Confusion Matrix -> TN={tn}  FP={fp}  FN={fn}  TP={tp}")

        # Overall pass/fail
        passed = (acc >= MIN_ACCURACY and f1 >= MIN_F1 and auc >= MIN_ROC_AUC)
        if passed:
            ok(f"{algo}: PASSED all thresholds")
        else:
            fail(f"{algo}: FAILED some thresholds")
            all_pass = False

        detailed.append({
            "algorithm": algo,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "roc_auc": auc,
            "train_acc": train_acc,
            "overfit_gap": gap,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "training_time_sec": r["training_time"],
            "passed": passed,
        })

    return detailed, all_pass


# ======================================================================
def step4_cross_validation(results, X_train, y_train):
    header("STEP 4 -- 5-Fold Stratified Cross-Validation")
    cv_results = []

    for r in results:
        algo  = r["algorithm"]
        model = r.get("model")
        if model is None:
            continue

        sub(algo.upper())
        for metric in ["f1", "accuracy", "roc_auc"]:
            cv = perform_cross_validation(
                model=model.__class__(**model.get_params()),
                X=X_train,
                y=y_train,
                cv=CV_FOLDS,
                scoring=metric,
            )
            folds_str = "  ".join([f"{s:.3f}" for s in cv["fold_scores"]])
            print(f"    [{metric:>8}] mean={cv['mean_score']:.4f} +/- {cv['std_score']:.4f}  | folds: [{folds_str}]")

        cv_results.append({"algorithm": algo, "cv_f1_mean": cv["mean_score"]})

    return cv_results


# ======================================================================
def step5_model_comparison(results):
    header("STEP 5 -- Model Comparison Ranking (sorted by F1)")
    comparison = compare_models(results)
    df_rank = comparison["ranking"]

    print(df_rank[["algorithm","accuracy","precision","recall","f1_score","roc_auc","training_time_sec"]].to_string())

    print(f"\n  Best Model: {comparison['best_algorithm']}")
    bm = comparison["best_metrics"]
    for k, v in bm.items():
        print(f"     {k}: {v:.4f}")

    return comparison


# ======================================================================
def step6_saved_model_check(X_test, y_test, feature_cols):
    header("STEP 6 -- Saved best_model.pkl Sanity Check")

    saved_dir = os.path.join(
        os.path.dirname(__file__), "..", "app", "ml", "saved_models"
    )
    model_path    = os.path.join(saved_dir, "best_model.pkl")
    scaler_path   = os.path.join(saved_dir, "scaler.pkl")
    metadata_path = os.path.join(saved_dir, "metadata.json")

    for path, label in [
        (model_path, "best_model.pkl"),
        (scaler_path, "scaler.pkl"),
        (metadata_path, "metadata.json"),
    ]:
        if os.path.exists(path):
            ok(f"{label} found ({os.path.getsize(path):,} bytes)")
        else:
            fail(f"{label} NOT FOUND at {path}")
            return

    # Load saved artefacts
    saved_model  = joblib.load(model_path)
    saved_scaler = joblib.load(scaler_path)
    with open(metadata_path) as f:
        meta = json.load(f)

    info(f"Saved algorithm   : {meta.get('algorithm', 'N/A')}")
    info(f"Saved metrics     : {meta.get('metrics', {})}")
    info(f"Saved version     : {meta.get('version', 'N/A')}")
    info(f"Feature count     : {len(meta.get('feature_columns', []))}")

    # Predict on fresh data
    df_test = generate_synthetic_dataset(n_samples=300, seed=99)
    feat_cols = meta.get("feature_columns", feature_cols)
    X_new = df_test[feat_cols]
    y_new = df_test["api_failure"].values

    X_new_scaled = saved_scaler.transform(X_new)
    y_pred = saved_model.predict(X_new_scaled)
    acc = float(np.mean(y_pred == y_new))
    ok(f"Saved model prediction accuracy on fresh data: {acc:.4f}")

    if acc >= MIN_ACCURACY:
        ok("Saved model passes accuracy threshold")
    else:
        fail(f"Saved model accuracy {acc:.4f} is BELOW threshold {MIN_ACCURACY}")

    # Reliability stats for 5 samples
    if hasattr(saved_model, "predict_proba"):
        proba = saved_model.predict_proba(X_new_scaled[:5])[:, 1]
        info("Reliability statistics for 5 sample predictions:")
        for i, p in enumerate(proba):
            stats = compute_reliability_statistics(float(p))
            print(f"    Sample {i+1}: failure_prob={p:.4f}  "
                  f"reliability_score={stats['reliability_score']}  "
                  f"MTBF={stats['mtbf_hours']:.1f}h")


# ======================================================================
def step7_feature_importance(results):
    header("STEP 7 -- Feature Importance (Tree-based Models)")
    feature_names = [
        "lines_of_code","cyclomatic_complexity","number_of_functions",
        "number_of_parameters","nested_depth","if_statement_count","loop_count",
        "imports_count","dependency_count","duplicate_code_score",
        "exception_handling_count","database_queries","external_api_calls",
        "cpu_usage","memory_usage","average_response_time",
        "test_coverage","historical_bug_count"
    ]

    tree_algos = ["random_forest","xgboost","lightgbm","catboost","decision_tree"]

    for r in results:
        algo  = r["algorithm"]
        model = r.get("model")
        if model is None or algo not in tree_algos:
            continue
        if not hasattr(model, "feature_importances_"):
            continue

        sub(f"Top-5 Features -- {algo.upper()}")
        importances = model.feature_importances_
        fi_pairs = sorted(zip(feature_names, importances), key=lambda x: -x[1])
        for name, imp in fi_pairs[:5]:
            bar = "#" * int(imp * 40)
            print(f"    {name:<32} {imp:.4f}  {bar}")


# ======================================================================
def step8_final_summary(detailed, all_pass):
    header("STEP 8 -- Final Summary Report")

    df = pd.DataFrame(detailed)
    passed = df[df["passed"] == True]
    failed = df[df["passed"] == False]

    print(f"\n  Total models evaluated : {len(df)}")
    print(f"  Passed                 : {len(passed)}")
    print(f"  Failed                 : {len(failed)}")

    if len(passed) > 0:
        best = df.loc[df["f1_score"].idxmax()]
        print(f"\n  Best model (highest F1): {best['algorithm']}")
        print(f"    Accuracy  : {best['accuracy']:.4f}")
        print(f"    F1-Score  : {best['f1_score']:.4f}")
        print(f"    ROC-AUC   : {best['roc_auc']:.4f}")
        print(f"    Overfit   : {best['overfit_gap']:+.4f}")

    if len(failed) > 0:
        print(f"\n  Models needing improvement:")
        for _, row in failed.iterrows():
            issues = []
            if row["accuracy"] < MIN_ACCURACY: issues.append(f"accuracy={row['accuracy']:.3f}<{MIN_ACCURACY}")
            if row["f1_score"]  < MIN_F1:       issues.append(f"f1={row['f1_score']:.3f}<{MIN_F1}")
            if row["roc_auc"]   < MIN_ROC_AUC:  issues.append(f"roc_auc={row['roc_auc']:.3f}<{MIN_ROC_AUC}")
            print(f"    - {row['algorithm']}: {', '.join(issues)}")

    print(f"\n  Thresholds used:")
    print(f"    Minimum Accuracy  >= {MIN_ACCURACY}")
    print(f"    Minimum F1-Score  >= {MIN_F1}")
    print(f"    Minimum ROC-AUC   >= {MIN_ROC_AUC}")
    print(f"    Max Overfit gap   <= {MAX_OVERFIT}")

    if all_pass:
        print(f"\n  [SUCCESS] ALL MODELS PASSED -- Pipeline is healthy!")
    else:
        print(f"\n  [WARNING] Some models need improvement. See details above.")


# ======================================================================
def main():
    print(f"\n{'='*60}")
    print(f"  Software Reliability -- Full Model Test Suite")
    print(f"{'='*60}")

    X_train, X_test, y_train, y_test, scaler, feature_cols = step1_generate_data()
    results, best_result, trainer = step2_train_all_models(X_train, X_test, y_train, y_test)
    detailed, all_pass = step3_evaluate_each_model(results, X_train, X_test, y_train, y_test)
    step4_cross_validation(results, X_train, y_train)
    step5_model_comparison(results)
    step6_saved_model_check(X_test, y_test, feature_cols)
    step7_feature_importance(results)
    step8_final_summary(detailed, all_pass)

    print(f"\n{'='*60}")
    print(f"  Test run complete.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

"""
Model loader for Software Reliability inference.

Loads serialized models, scalers, and metadata from disk.
"""

import os
import json
import joblib
from typing import Dict, Any, Optional, Tuple


SAVED_MODELS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "saved_models"
)


def load_model(model_dir: Optional[str] = None) -> Tuple[Any, Any, Dict[str, Any]]:
    """
    Load the best saved model, scaler, and metadata from disk.

    Args:
        model_dir: Path to the directory containing saved model artifacts.
                   Defaults to the standard saved_models directory.

    Returns:
        Tuple of (model, scaler, metadata_dict).

    Raises:
        FileNotFoundError: If required model files are missing.
    """
    if model_dir is None:
        model_dir = os.path.abspath(SAVED_MODELS_DIR)

    model_path = os.path.join(model_dir, "best_model.pkl")
    scaler_path = os.path.join(model_dir, "scaler.pkl")
    metadata_path = os.path.join(model_dir, "metadata.json")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No trained model found at {model_path}. "
            "Please train a model first using the /train endpoint."
        )

    model = joblib.load(model_path)

    scaler = None
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)

    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

    return model, scaler, metadata


def is_model_available(model_dir: Optional[str] = None) -> bool:
    """Check if a trained model is available on disk."""
    if model_dir is None:
        model_dir = os.path.abspath(SAVED_MODELS_DIR)

    model_path = os.path.join(model_dir, "best_model.pkl")
    return os.path.exists(model_path)

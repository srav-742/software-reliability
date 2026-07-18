"""
Prediction pipeline orchestrator for Software Reliability.
"""

from typing import Dict, Any

from app.ml.inference.predictor import reliability_predictor


def run_prediction_pipeline(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run prediction on a feature dictionary (standalone, no DB).

    Returns prediction result including risk level and reliability stats.
    """
    return reliability_predictor.predict(features)

"""
SHAP Summary Plot generator for Software Reliability.

Generates and saves SHAP beeswarm/summary plot images.
"""

import os
import numpy as np
from typing import Optional


def generate_summary_plot_data(
    shap_values: dict,
    feature_columns: list,
) -> dict:
    """
    Prepare summary plot data from SHAP values.

    Returns a serializable dict of sorted feature importances
    suitable for frontend chart rendering.
    """
    sorted_features = sorted(
        shap_values.items(),
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    return {
        "features": [f[0] for f in sorted_features],
        "values": [f[1] for f in sorted_features],
        "absolute_values": [abs(f[1]) for f in sorted_features],
    }

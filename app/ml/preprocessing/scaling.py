"""
Feature scaling utilities for the Software Reliability ML pipeline.

Provides StandardScaler and MinMaxScaler wrappers with serialization support.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Optional


class ReliabilityScaler:
    """
    Scaler wrapper that supports both StandardScaler and MinMaxScaler.
    Handles fitting, transforming, inverse transforming, and persistence.
    """

    def __init__(self, method: str = "standard"):
        """
        Args:
            method: 'standard' for StandardScaler, 'minmax' for MinMaxScaler.
        """
        if method == "standard":
            self.scaler = StandardScaler()
        elif method == "minmax":
            self.scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}. Use 'standard' or 'minmax'.")

        self.method = method
        self.is_fitted = False

    def fit(self, X: pd.DataFrame) -> "ReliabilityScaler":
        """Fit scaler on training data."""
        self.scaler.fit(X)
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform features using fitted scaler."""
        if not self.is_fitted:
            raise RuntimeError("Scaler has not been fitted yet. Call fit() first.")
        return self.scaler.transform(X)

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """Fit and transform in one step."""
        self.is_fitted = True
        return self.scaler.fit_transform(X)

    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """Reverse the scaling transformation."""
        return self.scaler.inverse_transform(X)

    def save(self, filepath: str) -> str:
        """Persist the fitted scaler to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.scaler, filepath)
        return filepath

    @classmethod
    def load(cls, filepath: str, method: str = "standard") -> "ReliabilityScaler":
        """Load a previously saved scaler from disk."""
        instance = cls(method=method)
        instance.scaler = joblib.load(filepath)
        instance.is_fitted = True
        return instance

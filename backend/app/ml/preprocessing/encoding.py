"""
Encoding utilities for categorical features in Software Reliability pipeline.

Handles label encoding for categorical project metadata (language, framework).
"""

import os
import joblib
from sklearn.preprocessing import LabelEncoder
from typing import Dict, List, Optional


class CategoryEncoder:
    """
    Label encoder wrapper for categorical project metadata fields.
    """

    def __init__(self):
        self.encoders: Dict[str, LabelEncoder] = {}

    def fit(self, column_name: str, values: List[str]) -> None:
        """Fit an encoder for a specific column."""
        encoder = LabelEncoder()
        encoder.fit(values)
        self.encoders[column_name] = encoder

    def transform(self, column_name: str, values: List[str]) -> List[int]:
        """Transform values using a fitted encoder."""
        if column_name not in self.encoders:
            raise ValueError(f"No encoder fitted for column: {column_name}")
        return self.encoders[column_name].transform(values).tolist()

    def save(self, filepath: str) -> str:
        """Save all encoders to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.encoders, filepath)
        return filepath

    @classmethod
    def load(cls, filepath: str) -> "CategoryEncoder":
        """Load encoders from disk."""
        instance = cls()
        instance.encoders = joblib.load(filepath)
        return instance

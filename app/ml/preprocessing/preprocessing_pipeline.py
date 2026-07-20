"""
Preprocessing pipeline orchestrator for Software Reliability ML pipeline.

Chains data cleaning, scaling, and train/test splitting into a single callable pipeline.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional

from app.ml.preprocessing.clean_data import clean_dataframe
from app.ml.preprocessing.scaling import ReliabilityScaler
from app.ml.preprocessing.split import split_dataset
from app.ml.datasets.generate_dataset import (
    generate_synthetic_dataset,
    save_dataset,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)


class PreprocessingPipeline:
    """
    End-to-end preprocessing pipeline:
    1. Load or generate dataset
    2. Clean data (handle NaN, cap outliers)
    3. Split into train/test
    4. Scale features
    """

    def __init__(self, scaler_method: str = "standard"):
        self.scaler = ReliabilityScaler(method=scaler_method)
        self.feature_columns = FEATURE_COLUMNS
        self.target_column = TARGET_COLUMN

    def load_dataset(self, csv_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load dataset from CSV, or generate a synthetic one if no path is given.
        """
        if csv_path and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            df = generate_synthetic_dataset(n_samples=3000)
            save_dataset(df)
        return df

    def run(
        self,
        csv_path: Optional[str] = None,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """
        Execute the full preprocessing pipeline.

        Returns:
            Dictionary containing:
                - X_train_scaled, X_test_scaled: np.ndarray
                - y_train, y_test: pd.Series
                - X_train, X_test: pd.DataFrame (unscaled)
                - scaler: fitted ReliabilityScaler
                - feature_columns: list of feature names
                - dataset_size: number of samples
        """
        # 1. Load
        df = self.load_dataset(csv_path)

        # 1b. Build derived interaction features
        from app.ml.feature_engineering.build_features import build_derived_features
        df = build_derived_features(df)
        self.feature_columns = [c for c in df.columns if c != self.target_column]

        # 2. Clean
        df = clean_dataframe(df, feature_columns=self.feature_columns)

        # 3. Ensure target column exists
        if self.target_column not in df.columns:
            raise ValueError(f"Target column '{self.target_column}' not found in dataset.")

        # 4. Split
        X_train, X_test, y_train, y_test = split_dataset(
            df,
            target_column=self.target_column,
            test_size=test_size,
            random_state=random_state,
            stratify=True,
        )

        # 5. Scale
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return {
            "X_train_scaled": X_train_scaled,
            "X_test_scaled": X_test_scaled,
            "y_train": y_train,
            "y_test": y_test,
            "X_train": X_train,
            "X_test": X_test,
            "scaler": self.scaler,
            "feature_columns": self.feature_columns,
            "dataset_size": len(df),
        }

    def preprocess_single_sample(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess a single feature dictionary (from a project's extracted metrics)
        for inference. Requires the scaler to already be fitted.
        """
        df = pd.DataFrame([features])

        # Ensure all feature columns are present
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0

        df = df[self.feature_columns]
        return self.scaler.transform(df)

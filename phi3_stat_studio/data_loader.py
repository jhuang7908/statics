"""Data import utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import pandas as pd


@dataclass
class DataFrameBundle:
    """Container for loaded dataset and metadata."""

    path: Optional[Path]
    dataframe: pd.DataFrame
    numeric_columns: List[str]
    categorical_columns: List[str]


class DataLoader:
    """Load CSV/Excel data for analysis."""

    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

    @staticmethod
    def load(path: Path) -> DataFrameBundle:
        if path.suffix.lower() not in DataLoader.SUPPORTED_EXTENSIONS:
            raise ValueError("Unsupported file type")

        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

        return DataFrameBundle(
            path=path,
            dataframe=df,
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols,
        )

    @staticmethod
    def load_sample() -> DataFrameBundle:
        sample_path = Path(__file__).resolve().parent / "assets" / "sample_data.csv"
        if not sample_path.exists():
            raise FileNotFoundError("Sample data missing")
        return DataLoader.load(sample_path)



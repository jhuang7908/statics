"""Descriptive statistics computations."""
from __future__ import annotations

from typing import Dict
import pandas as pd


def compute_descriptive_statistics(df: pd.DataFrame, column: str) -> Dict[str, float]:
    series = df[column].dropna()
    if series.empty:
        raise ValueError("Selected column has no valid data")

    stats = {
        "count": float(series.count()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std(ddof=1)),
        "min": float(series.min()),
        "max": float(series.max()),
        "q1": float(series.quantile(0.25)),
        "q3": float(series.quantile(0.75)),
    }
    return stats



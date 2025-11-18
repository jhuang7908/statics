"""T-test analysis functions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class TTestResult:
    statistic: float
    p_value: float
    df: float
    mean_difference: float
    confidence_interval: tuple[float, float]

    def to_dict(self) -> Dict[str, float]:
        return {
            "statistic": self.statistic,
            "p_value": self.p_value,
            "df": self.df,
            "mean_difference": self.mean_difference,
            "ci_lower": self.confidence_interval[0],
            "ci_upper": self.confidence_interval[1],
        }


def _confidence_interval(mean_diff: float, se: float, df: float, alpha: float = 0.05) -> tuple[float, float]:
    critical = stats.t.ppf(1 - alpha / 2, df)
    margin = critical * se
    return mean_diff - margin, mean_diff + margin


def one_sample_t_test(df: pd.DataFrame, column: str, population_mean: float = 0.0) -> TTestResult:
    series = df[column].dropna()
    if series.empty:
        raise ValueError("Selected column has no valid data")

    t_stat, p_value = stats.ttest_1samp(series, population_mean)
    dfree = len(series) - 1
    mean_diff = float(series.mean() - population_mean)
    se = float(series.std(ddof=1) / np.sqrt(len(series)))
    ci = _confidence_interval(mean_diff, se, dfree)

    return TTestResult(float(t_stat), float(p_value), float(dfree), mean_diff, ci)


def independent_t_test(
    df: pd.DataFrame,
    column: str,
    group_column: str,
    equal_var: bool = False,
) -> TTestResult:
    clean_df = df[[column, group_column]].dropna()
    groups = clean_df[group_column].unique()
    if len(groups) != 2:
        raise ValueError("Independent t-test requires exactly two groups")

    group_a = clean_df[clean_df[group_column] == groups[0]][column]
    group_b = clean_df[clean_df[group_column] == groups[1]][column]

    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=equal_var)

    n1, n2 = len(group_a), len(group_b)
    dfree = ((group_a.var(ddof=1) / n1) + (group_b.var(ddof=1) / n2)) ** 2
    dfree /= (
        ((group_a.var(ddof=1) / n1) ** 2) / (n1 - 1)
        + ((group_b.var(ddof=1) / n2) ** 2) / (n2 - 1)
    )

    mean_diff = float(group_a.mean() - group_b.mean())
    se = np.sqrt(group_a.var(ddof=1) / n1 + group_b.var(ddof=1) / n2)
    ci = _confidence_interval(mean_diff, se, dfree)

    return TTestResult(float(t_stat), float(p_value), float(dfree), mean_diff, ci)



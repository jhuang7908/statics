"""Plotting helpers."""
from __future__ import annotations

from io import BytesIO
from typing import Optional

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


sns.set_style("whitegrid")


def _apply_style(palette: Optional[str], font_size: Optional[int]) -> None:
    if font_size:
        plt.rcParams["font.size"] = font_size
    if palette:
        try:
            sns.set_palette(palette)
        except Exception:
            # Fallback silently if palette name is invalid
            pass


def _figure_to_bytes() -> bytes:
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    buffer.seek(0)
    return buffer.read()


def create_histogram(
    df: pd.DataFrame,
    column: str,
    title: Optional[str] = None,
    *,
    bins: Optional[int] = None,
    palette: Optional[str] = None,
    font_size: Optional[int] = None,
) -> bytes:
    _apply_style(palette, font_size)
    color = None
    if palette:
        try:
            color = sns.color_palette(palette)[0]
        except Exception:
            color = None
    sns.histplot(df[column].dropna(), kde=True, bins=bins, color=color)
    plt.title(title or f"Histogram of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    return _figure_to_bytes()


def create_scatter_plot(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: Optional[str] = None,
    *,
    point_size: Optional[int] = None,
    palette: Optional[str] = None,
    font_size: Optional[int] = None,
) -> bytes:
    _apply_style(palette, font_size)
    sns.scatterplot(data=df, x=x_column, y=y_column, s=point_size or 40)
    plt.title(title or f"Scatter Plot: {x_column} vs {y_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    return _figure_to_bytes()

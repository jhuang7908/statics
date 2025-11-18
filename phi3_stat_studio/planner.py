"""Task planner translating fuzzy instructions to structured commands."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import re


@dataclass
class AnalysisPlan:
    analysis_type: str
    target_column: Optional[str] = None
    group_column: Optional[str] = None
    reference_value: Optional[float] = None
    chart: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "analysis_type": self.analysis_type,
            "target_column": self.target_column,
            "group_column": self.group_column,
            "reference_value": self.reference_value,
            "chart": self.chart,
            "notes": self.notes,
        }


class RuleBasedPlanner:
    """Simple keyword-driven planner for Phase 0."""

    KEYWORDS = {
        "descriptive": ["描述", "概况", "平均", "统计", "summary"],
        "t_test_one_sample": ["单样本", "对比总体", "test mean"],
        "t_test_two_sample": ["比较", "两个组", "两组", "班级", "group"],
        "histogram": ["直方", "分布", "hist"],
        "scatter": ["相关", "散点", "关系", "scatter"],
    }

    @classmethod
    def plan(cls, instruction: str) -> AnalysisPlan:
        text = instruction.lower()

        for analysis, keywords in cls.KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                if analysis == "t_test_two_sample":
                    return AnalysisPlan(
                        analysis_type="t_test_two_sample",
                        group_column=None,
                        target_column=None,
                        notes="Detected comparison between two groups"
                    )
                if analysis == "t_test_one_sample":
                    reference = cls._extract_number(text)
                    return AnalysisPlan(
                        analysis_type="t_test_one_sample",
                        reference_value=reference,
                        notes="Detected one-sample t-test request"
                    )
                if analysis == "histogram":
                    return AnalysisPlan(analysis_type="descriptive", chart="histogram")
                if analysis == "scatter":
                    return AnalysisPlan(analysis_type="descriptive", chart="scatter")
                return AnalysisPlan(analysis_type="descriptive")
        return AnalysisPlan(analysis_type="descriptive", notes="Defaulted to descriptive analysis")

    @staticmethod
    def _extract_number(text: str) -> Optional[float]:
        match = re.search(r"(-?\d+\.?\d*)", text)
        if match:
            return float(match.group(1))
        return None



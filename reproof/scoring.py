"""Score aggregation for audit findings."""
from __future__ import annotations

from reproof.models import Dimension, Issue


DIMENSIONS = [
    ("environment", "环境可复现性", 20.0, "依赖版本、随机种子和运行环境"),
    ("data", "数据可获取性", 15.0, "数据路径和获取方式"),
    ("executable", "训练可执行性", 20.0, "入口和运行命令"),
    ("verifiable", "结果可验证性", 15.0, "结果记录与论文对应"),
    ("leakage", "数据泄漏风险", 15.0, "训练/测试数据隔离"),
    ("paper", "论文-代码一致", 15.0, "论文声明与代码实现"),
]
SEVERITY_DEDUCTION = {"high": 0.65, "medium": 0.35, "low": 0.15, "info": 0.0}


def compute_dimensions(issues: list[Issue]) -> list[Dimension]:
    dimensions: list[Dimension] = []
    for key, label, maximum, description in DIMENSIONS:
        score = maximum
        matched = [issue for issue in issues if issue.category == key]
        for issue in matched:
            score -= maximum * SEVERITY_DEDUCTION.get(issue.severity, 0.2)
        dimensions.append(Dimension(key, label, max(0.0, round(score, 1)), maximum, description))
    return dimensions


def grade_for(score: float) -> tuple[str, str]:
    if score >= 85:
        return "A · 低风险", "可复现性风险较低，仍建议人工确认中低优先级问题。"
    if score >= 70:
        return "B · 需关注", "存在一定复现风险，建议优先修复高风险问题后提交。"
    if score >= 50:
        return "C · 高风险", "存在多个高风险问题，不建议直接提交 Artifact。"
    return "D · 严重风险", "仓库当前存在严重可复现性风险，需要系统性修复。"

"""Markdown report."""
from __future__ import annotations

from pathlib import Path

from reproof.models import AuditResult


def render_markdown(result: AuditResult) -> str:
    counts = {
        "high": sum(1 for issue in result.issues if issue.severity == "high"),
        "medium": sum(1 for issue in result.issues if issue.severity == "medium"),
        "low": sum(1 for issue in result.issues if issue.severity == "low"),
    }
    lines = [
        "# ReproProof 可复现性审计报告",
        "",
        f"- 仓库：`{result.repository}`",
        f"- 生成时间：{result.generated_at}",
        f"- 综合评分：**{result.score}/100**",
        f"- 风险等级：**{result.grade}**",
        f"- 问题数量：{len(result.issues)}（高 {counts['high']} / 中 {counts['medium']} / 低 {counts['low']}）",
        "",
        f"> {result.recommendation}",
        "",
        "## 维度评分",
        "",
        "| 维度 | 得分 | 满分 | 说明 |",
        "|---|---:|---:|---|",
    ]
    for dimension in result.dimensions:
        lines.append(f"| {dimension.label} | {dimension.score} | {dimension.max_score} | {dimension.description} |")
    lines += ["", "## 问题列表", ""]
    if not result.issues:
        lines.append("未发现规则覆盖范围内的问题。")
    for index, issue in enumerate(result.issues, start=1):
        location = issue.file + (f":{issue.line}" if issue.line else "")
        lines += [
            f"### {index}. [{issue.severity.upper()}] {issue.title}",
            "",
            f"- 规则：`{issue.rule_id}`",
            f"- 位置：`{location}`",
            f"- 置信度：{int(issue.confidence * 100)}%",
            f"- 说明：{issue.message}",
        ]
        if issue.evidence:
            lines.append(f"- 证据：`{issue.evidence}`")
        if issue.suggestion:
            lines.append(f"- 建议：{issue.suggestion}")
        lines.append("")
    lines += [
        "## 说明",
        "",
        "本报告是基于规则和有限文本/代码分析的辅助审计结果，不代表会议或期刊的正式评审结论。",
        "论文-代码一致性检测只覆盖可解释、有证据的有限场景，需要用户人工确认。",
    ]
    return "\n".join(lines)


def write_markdown(result: AuditResult, output: Path) -> Path:
    output.write_text(render_markdown(result), encoding="utf-8")
    return output

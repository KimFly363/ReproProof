"""PR comment rendering."""
from __future__ import annotations

from pathlib import Path

from reproof.models import AuditResult


def render_pr_comment(result: AuditResult) -> str:
    high = sum(1 for issue in result.issues if issue.severity == "high")
    medium = sum(1 for issue in result.issues if issue.severity == "medium")
    lines = [
        "## ReproProof 可复现性审计",
        "",
        f"**评分：{result.score}/100 · {result.grade}**",
        "",
        f"本次检查发现 **{high} 个高优先级**、**{medium} 个中优先级**问题。",
        "",
    ]
    if not result.issues:
        lines.append("未发现规则覆盖范围内的问题。")
    for issue in result.issues[:8]:
        location = f"`{issue.file}`" + (f":{issue.line}" if issue.line else "")
        lines += [
            f"### [{issue.severity.upper()}] {issue.title}",
            "",
            f"- 位置：{location}",
            f"- 说明：{issue.message}",
        ]
        if issue.evidence:
            lines.append(f"- 证据：`{issue.evidence}`")
        if issue.suggestion:
            lines.append(f"- 建议：{issue.suggestion}")
        lines.append("")
    if len(result.issues) > 8:
        lines.append(f"还有 {len(result.issues) - 8} 个问题，请查看完整报告。")
    lines += ["", "> 结果仅供辅助检查，请人工确认。"]
    return "\n".join(lines)


def write_pr_comment(result: AuditResult, output: Path) -> Path:
    output.write_text(render_pr_comment(result), encoding="utf-8")
    return output

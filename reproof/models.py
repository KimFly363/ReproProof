"""Core data models for ReproProof."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1, "info": 0}


@dataclass
class Issue:
    rule_id: str
    title: str
    severity: str
    category: str
    file: str
    line: int | None
    message: str
    evidence: str = ""
    suggestion: str = ""
    confidence: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Dimension:
    key: str
    label: str
    score: float
    max_score: float
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditResult:
    repository: str
    generated_at: str
    issues: list[Issue]
    score: float
    grade: str
    recommendation: str
    dimensions: list[Dimension]
    rules_run: list[str]
    paper: str | None = None
    stats: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["summary"] = {
            "total": len(self.issues),
            "high": sum(1 for issue in self.issues if issue.severity == "high"),
            "medium": sum(1 for issue in self.issues if issue.severity == "medium"),
            "low": sum(1 for issue in self.issues if issue.severity == "low"),
        }
        return data


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sort_issues(issues: list[Issue]) -> list[Issue]:
    return sorted(
        issues,
        key=lambda issue: (
            -SEVERITY_ORDER.get(issue.severity, 0),
            issue.rule_id,
            issue.file,
            issue.line or 0,
        ),
    )

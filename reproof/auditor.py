"""Audit orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reproof.analyzers.file_scanner import Repository
from reproof.analyzers.paper_parser import load_paper_text
from reproof.models import AuditResult, Issue, sort_issues, utc_now_iso
from reproof.rules.data_leak_check import DataLeakageRule
from reproof.rules.dependency_check import DependencyCheckRule
from reproof.rules.hardcode_path_check import HardcodedPathRule
from reproof.rules.paper_consistency import PaperConsistencyRule
from reproof.rules.readme_entry_check import ReadmeEntryRule
from reproof.rules.seed_check import SeedCheckRule
from reproof.scoring import compute_dimensions, grade_for


RULES = [
    SeedCheckRule(),
    DependencyCheckRule(),
    HardcodedPathRule(),
    DataLeakageRule(),
    ReadmeEntryRule(),
    PaperConsistencyRule(),
]


@dataclass
class AuditOptions:
    fail_on: str = "high"
    paper_path: str | None = None


def audit_repository(repository_path: str | Path, options: AuditOptions | None = None) -> AuditResult:
    options = options or AuditOptions()
    repo = Repository(repository_path)
    paper_text = load_paper_text(options.paper_path) if options.paper_path else ""
    issues: list[Issue] = []
    rules_run: list[str] = []
    for rule in RULES:
        rules_run.append(rule.rule_id)
        try:
            issues.extend(rule.run(repo, paper_text))
        except Exception as exc:  # keep the audit running if one rule fails
            issues.append(
                Issue(
                    rule_id=rule.rule_id,
                    title=f"{rule.title}（规则执行异常）",
                    severity="medium",
                    category=rule.category,
                    file=".",
                    line=None,
                    message=f"规则执行失败：{type(exc).__name__}: {exc}",
                    suggestion="请检查仓库文件或提交 issue。",
                    confidence=0.1,
                )
            )
    issues = sort_issues(issues)
    dimensions = compute_dimensions(issues)
    high_count = sum(1 for issue in issues if issue.severity == 'high')
    medium_count = sum(1 for issue in issues if issue.severity == 'medium')
    low_count = sum(1 for issue in issues if issue.severity == 'low')
    dimension_score = sum(dimension.score for dimension in dimensions)
    penalty_score = 100 - (18 * high_count + 8 * medium_count + 3 * low_count)
    score = round(min(dimension_score, max(0, penalty_score)), 1)
    grade, recommendation = grade_for(score)
    return AuditResult(
        repository=str(repo.root),
        generated_at=utc_now_iso(),
        issues=issues,
        score=score,
        grade=grade,
        recommendation=recommendation,
        dimensions=dimensions,
        rules_run=rules_run,
        paper=str(Path(options.paper_path).resolve()) if options.paper_path else None,
        stats={
            "files_scanned": len(repo.files),
            "python_files": len(repo.python_files),
            "readme_files": len(repo.readmes),
            "dependency_files": len(repo.dependency_files),
            "paper_loaded": bool(paper_text),
        },
    )

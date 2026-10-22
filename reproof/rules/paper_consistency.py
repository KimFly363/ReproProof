"""Rule 6: limited paper/code dataset and metric consistency checks."""
from __future__ import annotations

from reproof.analyzers.file_scanner import Repository
from reproof.analyzers.paper_parser import extract_context, extract_datasets, extract_metrics
from reproof.data.catalog import CODE_DATASET_HINTS, CODE_METRIC_HINTS, DATASET_ALIASES, METRIC_ALIASES
from reproof.models import Issue
from reproof.rules.base import Rule


def _find_hint(repo: Repository, aliases: list[str]):
    ignored_names = ('paper', 'readme', 'license')
    allowed_suffixes = {'.py', '.yaml', '.yml', '.json', '.toml', '.cfg', '.ini'}
    for file in repo.files:
        if file.path.name.lower().startswith(ignored_names) or file.suffix not in allowed_suffixes:
            continue
        lower_lines = file.text.lower().splitlines()
        for index, line in enumerate(lower_lines, start=1):
            for alias in aliases:
                if alias.lower() in line:
                    return file.relative_path, index, line.strip()
    return None


class PaperConsistencyRule(Rule):
    rule_id = "R6"
    title = "论文-代码数据集/指标不一致"
    category = "paper"
    severity = "high"

    def run(self, repo: Repository, paper_text: str = "") -> list[Issue]:
        if not paper_text.strip():
            return []

        paper_datasets = extract_datasets(paper_text)
        paper_metrics = extract_metrics(paper_text)
        code_datasets = [
            name for name, aliases in CODE_DATASET_HINTS.items()
            if _find_hint(repo, aliases) is not None
        ]
        code_metrics = [
            name for name, aliases in CODE_METRIC_HINTS.items()
            if _find_hint(repo, aliases) is not None
        ]
        issues: list[Issue] = []

        if paper_datasets:
            if not code_datasets:
                issues.append(self._issue(
                    message=f"论文声明使用 {', '.join(paper_datasets)}，但代码中未识别到明确的数据集加载。",
                    evidence=extract_context(paper_text, DATASET_ALIASES[paper_datasets[0]]),
                    suggestion="在代码或配置中明确声明数据集名称，并确保与论文一致。",
                    confidence=0.65,
                ))
            else:
                missing = [name for name in paper_datasets if name not in code_datasets]
                if missing:
                    code_evidence = _find_hint(repo, CODE_DATASET_HINTS[code_datasets[0]])
                    file, line, source = code_evidence if code_evidence else (".", None, "")
                    issues.append(self._issue(
                        message=f"论文声明数据集 {', '.join(missing)}，代码中识别到 {', '.join(code_datasets)}。",
                        evidence=f"论文：{extract_context(paper_text, DATASET_ALIASES[missing[0]])} | 代码：{source}",
                        suggestion="确认论文与代码使用同一数据集，或更新论文/配置中的数据集声明。",
                        confidence=0.8,
                        file=file,
                        line=line,
                    ))

        if paper_metrics:
            if not code_metrics:
                issues.append(self._issue(
                    message=f"论文报告指标 {', '.join(paper_metrics)}，但代码中未识别到对应指标计算。",
                    evidence=extract_context(paper_text, METRIC_ALIASES[paper_metrics[0]]),
                    suggestion="确认评估代码是否计算论文声明的指标，并统一指标名称和计算方式。",
                    confidence=0.62,
                ))
            else:
                missing = [name for name in paper_metrics if name not in code_metrics]
                if missing:
                    code_evidence = _find_hint(repo, CODE_METRIC_HINTS[code_metrics[0]])
                    file, line, source = code_evidence if code_evidence else (".", None, "")
                    issues.append(self._issue(
                        message=f"论文报告指标 {', '.join(missing)}，代码中识别到 {', '.join(code_metrics)}。",
                        evidence=f"论文：{extract_context(paper_text, METRIC_ALIASES[missing[0]])} | 代码：{source}",
                        suggestion="确认评估脚本是否实际计算并记录了论文声明的指标。",
                        confidence=0.76,
                        file=file,
                        line=line,
                    ))
        return issues

    def _issue(self, message, evidence, suggestion, confidence, file="paper", line=None):
        return Issue(
            rule_id=self.rule_id,
            title=self.title,
            severity=self.severity,
            category=self.category,
            file=file,
            line=line,
            message=message,
            evidence=evidence,
            suggestion=suggestion,
            confidence=confidence,
        )

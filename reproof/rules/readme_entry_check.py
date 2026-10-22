"""Rule 5: compare README commands with repository entry files."""
from __future__ import annotations

import re

from reproof.analyzers.file_scanner import Repository
from reproof.models import Issue
from reproof.rules.base import Rule


COMMAND_RE = re.compile(r"python(?:3)?\s+([^\s`]+\.py)", re.IGNORECASE)


class ReadmeEntryRule(Rule):
    rule_id = "R5"
    title = "README 入口不一致"
    category = "executable"
    severity = "medium"

    def run(self, repo: Repository, paper_text: str = "") -> list[Issue]:
        entry_names = {"train.py", "main.py", "run.py", "fit.py", "experiment.py"}
        root_entries = [
            file for file in repo.python_files
            if "/" not in file.relative_path and file.path.name.lower() in entry_names
        ]
        # README run-command rules only apply to repositories with a clear root entrypoint.
        if not root_entries:
            return []
        if not repo.readmes:
            return [
                Issue(
                    rule_id=self.rule_id,
                    title=self.title,
                    severity=self.severity,
                    category=self.category,
                    file="README.md",
                    line=None,
                    message="仓库缺少 README，无法确认运行入口和实验命令。",
                    suggestion="补充环境安装、训练、评估和复现实验的命令。",
                    confidence=0.95,
                )
            ]
        issues: list[Issue] = []
        commands_found = 0
        for readme in repo.readmes:
            lines = readme.text.splitlines()
            for index, line in enumerate(lines, start=1):
                match = COMMAND_RE.search(line)
                if not match:
                    continue
                commands_found += 1
                target = match.group(1).strip().strip("'\"")
                if target.startswith("./"):
                    target = target[2:]
                if not repo.find(target) and not (repo.root / target).exists():
                    issues.append(
                        Issue(
                            rule_id=self.rule_id,
                            title=self.title,
                            severity=self.severity,
                            category=self.category,
                            file=readme.relative_path,
                            line=index,
                            message=f"README 中声明的入口文件不存在：{target}",
                            evidence=line.strip(),
                            suggestion="修正 README 命令，或补充缺失的运行脚本。",
                            confidence=0.96,
                            metadata={"target": target},
                        )
                    )
        if commands_found == 0:
            issues.append(
                Issue(
                    rule_id=self.rule_id,
                    title=self.title,
                    severity=self.severity,
                    category=self.category,
                    file=repo.readmes[0].relative_path,
                    line=None,
                    message="README 中没有发现 python xxx.py 形式的运行命令。",
                    suggestion="明确写出安装、训练和评估命令。",
                    confidence=0.85,
                )
            )
        return issues

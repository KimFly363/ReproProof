"""Rule 3: detect machine-specific absolute paths in Python code."""
from __future__ import annotations

import ast
import re

from reproof.analyzers.file_scanner import Repository
from reproof.models import Issue
from reproof.rules.base import Rule


WINDOWS_PATH = re.compile(r"^[A-Za-z]:[\\/]")
POSIX_PERSONAL_PATH = re.compile(r"^/(?:home|Users|mnt|Volumes)/")
NETWORK_PATH = re.compile(r"^\\\\[^\\]+\\")
IGNORED_PREFIXES = ("/tmp/", "/dev/", "/proc/")


class HardcodedPathRule(Rule):
    rule_id = "R3"
    title = "数据路径硬编码"
    category = "data"
    severity = "high"

    def run(self, repo: Repository, paper_text: str = "") -> list[Issue]:
        issues: list[Issue] = []
        for file in repo.python_files:
            try:
                tree = ast.parse(file.text, filename=file.relative_path)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                    continue
                value = node.value
                if value.startswith(("http://", "https://")) or value.startswith(IGNORED_PREFIXES):
                    continue
                if WINDOWS_PATH.match(value) or POSIX_PERSONAL_PATH.match(value) or NETWORK_PATH.match(value):
                    lines = file.text.splitlines()
                    evidence = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else value
                    issues.append(
                        Issue(
                            rule_id=self.rule_id,
                            title=self.title,
                            severity=self.severity,
                            category=self.category,
                            file=file.relative_path,
                            line=node.lineno,
                            message=f"发现机器相关的绝对路径：{value}",
                            evidence=evidence,
                            suggestion="通过配置文件、环境变量或命令行参数传入数据路径。",
                            confidence=0.98,
                        )
                    )
                    break
        return issues

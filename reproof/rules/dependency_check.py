"""Rule 2: detect dependency manifests without locked versions."""
from __future__ import annotations

import re

from reproof.analyzers.file_scanner import Repository
from reproof.models import Issue
from reproof.rules.base import Rule


LOCK_FILES = {"poetry.lock", "pipfile.lock", "conda-lock.yml", "uv.lock", "pylock.toml", "requirements.lock"}
MANIFESTS = {"requirements.txt", "pyproject.toml", "environment.yml", "environment.yaml", "pipfile"}


class DependencyCheckRule(Rule):
    rule_id = "R2"
    title = "依赖版本未锁定"
    category = "environment"
    severity = "high"

    def run(self, repo: Repository, paper_text: str = "") -> list[Issue]:
        files = repo.dependency_files
        if not files:
            return [
                Issue(
                    rule_id=self.rule_id,
                    title=self.title,
                    severity=self.severity,
                    category=self.category,
                    file=".",
                    line=None,
                    message="未找到 requirements.txt、pyproject.toml、environment.yml 等依赖清单。",
                    evidence="",
                    suggestion="提供 requirements.txt 或 pyproject.toml，并使用精确版本或锁文件。",
                    confidence=0.96,
                )
            ]

        if any(file.path.name.lower() in LOCK_FILES for file in files):
            return []

        manifest = next((file for file in files if file.path.name.lower() in MANIFESTS or file.path.name.lower().startswith("requirements")), files[0])
        unpinned: list[tuple[int, str]] = []
        if manifest.path.name.lower().startswith("requirements") or manifest.path.name.lower() == "requirements.txt":
            for index, line in enumerate(manifest.text.splitlines(), start=1):
                value = line.split("#", 1)[0].strip()
                if not value or value.startswith(("-", "git+", "http://", "https://")):
                    continue
                if re.match(r"^[A-Za-z0-9_.-]+(?:\[[^\]]+\])?\s*(==|===|@)", value):
                    continue
                if re.match(r"^[A-Za-z0-9_.-]+", value):
                    unpinned.append((index, value))
        else:
            for index, line in enumerate(manifest.text.splitlines(), start=1):
                stripped = line.strip()
                if re.match(r"^[A-Za-z0-9_.-]+\s*(>=|<=|~=|>|<|\^)", stripped):
                    unpinned.append((index, stripped))

        if not unpinned:
            return []
        first_line, first_value = unpinned[0]
        names = ", ".join(value for _, value in unpinned[:4])
        return [
            Issue(
                rule_id=self.rule_id,
                title=self.title,
                severity=self.severity,
                category=self.category,
                file=manifest.relative_path,
                line=first_line,
                message=f"发现 {len(unpinned)} 个未锁定版本的依赖：{names}。",
                evidence=first_value,
                suggestion="使用 package==version、锁文件（poetry.lock/uv.lock 等）或容器镜像固定运行环境。",
                confidence=0.9,
                metadata={"unpinned": [value for _, value in unpinned[:20]]},
            )
        ]

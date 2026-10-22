"""Repository file discovery and safe text loading."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    "node_modules", "dist", "build", ".tox", ".mypy_cache", ".ruff_cache",
}
TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".cfg", ".ini", ".sh", ".bat",
}
MAX_FILE_BYTES = 1_000_000


@dataclass(frozen=True)
class RepoFile:
    path: Path
    relative_path: str
    text: str
    suffix: str


class Repository:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        if not self.root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.root}")
        if not self.root.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {self.root}")
        self.files = self._scan()

    def _scan(self) -> list[RepoFile]:
        results: list[RepoFile] = []
        for path in self.root.rglob("*"):
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            results.append(
                RepoFile(
                    path=path,
                    relative_path=path.relative_to(self.root).as_posix(),
                    text=text,
                    suffix=path.suffix.lower(),
                )
            )
        return sorted(results, key=lambda item: item.relative_path)

    @property
    def python_files(self) -> list[RepoFile]:
        return [file for file in self.files if file.suffix == ".py"]

    @property
    def readmes(self) -> list[RepoFile]:
        return [file for file in self.files if file.path.name.lower().startswith("readme")]

    @property
    def dependency_files(self) -> list[RepoFile]:
        names = {
            "requirements.txt", "pyproject.toml", "environment.yml", "environment.yaml",
            "pipfile", "poetry.lock", "pipfile.lock", "conda-lock.yml", "uv.lock",
        }
        return [
            file for file in self.files
            if file.path.name.lower() in names or file.path.name.lower().startswith("requirements")
        ]

    def find(self, relative_path: str) -> RepoFile | None:
        target = relative_path.replace("\\", "/").lstrip("./")
        return next((file for file in self.files if file.relative_path == target), None)

    def all_text(self) -> str:
        return "\n".join(file.text for file in self.files)

    def source_evidence(self, relative_path: str, line: int | None = None) -> str:
        file = self.find(relative_path)
        if not file:
            return ""
        lines = file.text.splitlines()
        if line and 1 <= line <= len(lines):
            return lines[line - 1].strip()
        return ""

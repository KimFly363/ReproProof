"""Paper text loading and lightweight extraction."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reproof.data.catalog import DATASET_ALIASES, METRIC_ALIASES


def load_paper_text(path: str | Path | None) -> str:
    if not path:
        return ""
    paper = Path(path)
    if not paper.exists():
        raise FileNotFoundError(f"Paper does not exist: {paper}")
    suffix = paper.suffix.lower()
    if suffix in {".txt", ".md"}:
        return paper.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            vendor = Path(__file__).resolve().parents[2] / "vendor"
            if vendor.exists():
                sys.path.insert(0, str(vendor))
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise RuntimeError("PDF parsing requires pypdf. The bundled vendor/pypdf directory was not found.") from exc
        reader = PdfReader(str(paper))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"Unsupported paper format: {paper.suffix}")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def find_alias(haystack: str, alias: str) -> int:
    pattern = r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])"
    match = re.search(pattern, haystack)
    return match.start() if match else -1


def extract_datasets(text: str) -> list[str]:
    haystack = normalize(text)
    found: list[tuple[int, str]] = []
    for canonical, aliases in DATASET_ALIASES.items():
        positions = [find_alias(haystack, alias) for alias in aliases]
        positions = [position for position in positions if position >= 0]
        if positions:
            found.append((min(positions), canonical))
    return [name for _, name in sorted(found)]


def extract_metrics(text: str) -> list[str]:
    haystack = normalize(text)
    found: list[tuple[int, str]] = []
    for canonical, aliases in METRIC_ALIASES.items():
        positions = [find_alias(haystack, alias) for alias in aliases]
        positions = [position for position in positions if position >= 0]
        if positions:
            found.append((min(positions), canonical))
    return [name for _, name in sorted(found)]


def extract_context(text: str, aliases: list[str], window: int = 80) -> str:
    haystack = normalize(text)
    for alias in aliases:
        index = find_alias(haystack, alias)
        if index >= 0:
            start = max(0, index - window // 2)
            end = min(len(haystack), index + len(alias) + window)
            return haystack[start:end].strip()
    return ""

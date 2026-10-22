"""Base rule protocol."""
from __future__ import annotations

from abc import ABC, abstractmethod

from reproof.analyzers.file_scanner import Repository
from reproof.models import Issue


class Rule(ABC):
    rule_id: str
    title: str
    category: str
    severity: str = "medium"

    @abstractmethod
    def run(self, repo: Repository, paper_text: str = "") -> list[Issue]:
        raise NotImplementedError

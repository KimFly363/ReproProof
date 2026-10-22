"""JSON report."""
from __future__ import annotations

import json
from pathlib import Path

from reproof.models import AuditResult


def render_json(result: AuditResult) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)


def write_json(result: AuditResult, output: Path) -> Path:
    output.write_text(render_json(result), encoding="utf-8")
    return output

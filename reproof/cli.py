"""ReproProof command line interface."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reproof import __version__
from reproof.auditor import AuditOptions, audit_repository
from reproof.models import SEVERITY_ORDER
from reproof.reporters.html_reporter import write_html
from reproof.reporters.json_reporter import write_json
from reproof.reporters.markdown_reporter import write_markdown
from reproof.reporters.pr_comment_reporter import write_pr_comment


FORMAT_WRITERS = {
    "html": ("report.html", write_html),
    "md": ("report.md", write_markdown),
    "json": ("report.json", write_json),
    "pr": ("pr-comment.md", write_pr_comment),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reproof",
        description="ReproProof: AI 论文 Artifact 提交前的可复现性审计工具",
    )
    parser.add_argument("--version", action="version", version=f"reproof {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit", help="审计一个 Python ML 仓库")
    audit.add_argument("path", nargs="?", default=".", help="仓库目录，默认当前目录")
    audit.add_argument("--paper", help="可选论文 PDF/TXT/MD 路径")
    audit.add_argument("--out", default="reproof-report", help="报告输出目录")
    audit.add_argument("--format", default="html,md,json,pr", help="报告格式，逗号分隔：html,md,json,pr")
    audit.add_argument("--fail-on", choices=["none", "high", "medium", "low"], default="high", help="发现达到该级别的问题时返回非零退出码")
    audit.add_argument("--quiet", action="store_true", help="只输出摘要")
    return parser


def _threshold(fail_on: str) -> int:
    return {"none": 0, "high": 3, "medium": 2, "low": 1}[fail_on]


def _should_fail(result, fail_on: str) -> bool:
    threshold = _threshold(fail_on)
    if threshold == 0:
        return False
    return any(SEVERITY_ORDER.get(issue.severity, 0) >= threshold for issue in result.issues)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "audit":
        parser.print_help()
        return 2

    formats = [value.strip().lower() for value in args.format.split(",") if value.strip()]
    unknown = [value for value in formats if value not in FORMAT_WRITERS]
    if unknown:
        parser.error(f"不支持的报告格式：{', '.join(unknown)}")

    try:
        result = audit_repository(args.path, AuditOptions(fail_on=args.fail_on, paper_path=args.paper))
    except Exception as exc:
        print(f"ReproProof audit failed: {exc}", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name in formats:
        filename, writer = FORMAT_WRITERS[name]
        written.append(writer(result, out_dir / filename))

    if not args.quiet:
        print("\nReproProof 可复现性审计")
        print(f"仓库: {result.repository}")
        print(f"评分: {result.score}/100 · {result.grade}")
        print(f"问题: {len(result.issues)} 条")
        for issue in result.issues:
            location = issue.file + (f":{issue.line}" if issue.line else "")
            print(f"  [{issue.severity.upper():6}] {issue.rule_id} {issue.title} · {location}")
        print(f"建议: {result.recommendation}")
        print("报告:")
        for path in written:
            print(f"  - {path}")

    return 1 if _should_fail(result, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Self-contained HTML report."""
from __future__ import annotations

import html
from pathlib import Path

from reproof.models import AuditResult


def _e(value) -> str:
    return html.escape(str(value or ""))


def render_html(result: AuditResult) -> str:
    high = sum(1 for issue in result.issues if issue.severity == "high")
    medium = sum(1 for issue in result.issues if issue.severity == "medium")
    low = sum(1 for issue in result.issues if issue.severity == "low")
    dimensions = "\n".join(
        f'''<div class="dimension">
          <div class="dimension-head"><span>{_e(dim.label)}</span><strong>{dim.score:.1f}/{dim.max_score:.0f}</strong></div>
          <div class="dimension-track"><i style="width:{max(0, dim.score / dim.max_score * 100):.1f}%"></i></div>
          <p>{_e(dim.description)}</p>
        </div>'''
        for dim in result.dimensions
    )
    issues = []
    for index, issue in enumerate(result.issues, start=1):
        location = issue.file + (f":{issue.line}" if issue.line else "")
        evidence = f'<div class="issue-evidence"><span>证据</span><code>{_e(issue.evidence)}</code></div>' if issue.evidence else ""
        suggestion = f'<div class="issue-suggestion"><span>修复建议</span><p>{_e(issue.suggestion)}</p></div>' if issue.suggestion else ""
        issues.append(f"""
        <article class="issue issue-{_e(issue.severity)}">
          <div class="issue-index">{index:02d}</div>
          <div class="issue-body">
            <div class="issue-meta"><span class="severity">{_e(issue.severity.upper())}</span><span>{_e(issue.rule_id)}</span><span>{_e(location)}</span><span>置信度 {int(issue.confidence * 100)}%</span></div>
            <h3>{_e(issue.title)}</h3>
            <p class="issue-message">{_e(issue.message)}</p>
            {evidence}
            {suggestion}
          </div>
        </article>""")
    issue_html = "\n".join(issues) or '<div class="empty">未发现规则覆盖范围内的问题。</div>'
    stats = result.stats
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ReproProof 可复现性审计报告</title>
<style>
:root{{--ink:#181632;--muted:#6f6b86;--line:#ddd9ef;--paper:#fff;--canvas:#f3f2f8;--indigo:#5546c8;--indigo-dark:#312577;--violet:#ece9fb;--red:#c54d57;--amber:#b87919;--green:#2d8060;--slate:#697386;--mono:Consolas,"SFMono-Regular",monospace;--sans:"Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;--serif:"Noto Serif SC","Songti SC",serif}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--canvas);color:var(--ink);font-family:var(--sans);line-height:1.7}}.page{{max-width:1120px;margin:0 auto;padding:28px 22px 54px}}.hero{{position:relative;padding:30px 32px;color:#f9f8ff;background:linear-gradient(130deg,#252057,#5546c8);overflow:hidden}}.hero:after{{content:"";position:absolute;right:-90px;top:-100px;width:320px;height:320px;border:1px solid rgba(255,255,255,.17);border-radius:50%;box-shadow:0 0 0 45px rgba(255,255,255,.03),0 0 0 90px rgba(255,255,255,.025)}}.brand{{font-size:11px;letter-spacing:.16em;color:rgba(255,255,255,.6)}}.hero h1{{position:relative;z-index:1;margin:10px 0 6px;font-family:var(--serif);font-size:30px;line-height:1.3}}.hero p{{position:relative;z-index:1;margin:0;max-width:720px;color:rgba(255,255,255,.62);font-size:11px}}.hero-grid{{position:relative;z-index:1;display:grid;grid-template-columns:1fr 190px;gap:22px;align-items:end;margin-top:28px}}.meta{{display:flex;flex-wrap:wrap;gap:14px;color:rgba(255,255,255,.48);font-size:9px}}.score-card{{padding:20px;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.17)}}.score-card strong{{display:block;font-family:var(--serif);font-size:52px;line-height:1;color:#fff}}.score-card strong small{{font-family:var(--sans);font-size:13px;color:rgba(255,255,255,.55)}}.score-card span{{display:block;margin-top:8px;color:#d8d2ff;font-size:10px}}.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;margin:18px 0;background:var(--line);border:1px solid var(--line)}}.summary div{{padding:15px 17px;background:#fff}}.summary strong{{display:block;font-family:var(--serif);font-size:25px;line-height:1.1}}.summary span{{display:block;margin-top:4px;color:var(--muted);font-size:8px}}.grid{{display:grid;grid-template-columns:340px minmax(0,1fr);gap:18px;align-items:start}}.card{{padding:20px;background:var(--paper);border:1px solid var(--line)}}.card h2{{margin:0 0 14px;font-family:var(--serif);font-size:18px;border:0;padding:0}}.dimension{{padding:11px 0;border-top:1px solid #ebe8f4}}.dimension:first-of-type{{border-top:0}}.dimension-head{{display:flex;justify-content:space-between;gap:12px;font-size:10px}}.dimension-head strong{{font-weight:500;color:var(--indigo)}}.dimension-track{{height:5px;margin-top:7px;background:#eceaf6;overflow:hidden}}.dimension-track i{{display:block;height:100%;background:linear-gradient(90deg,var(--indigo),#8e80ef)}}.dimension p{{margin:5px 0 0;color:var(--muted);font-size:8px}}.stat-list{{display:grid;grid-template-columns:1fr 1fr;gap:1px;margin-top:16px;background:var(--line)}}.stat-list div{{padding:10px;background:#faf9fd}}.stat-list b{{display:block;font-size:15px}}.stat-list span{{color:var(--muted);font-size:8px}}.issues-head{{display:flex;justify-content:space-between;align-items:baseline;margin:0 0 10px}}.issues-head h2{{margin:0;font-family:var(--serif);font-size:20px}}.issues-head span{{color:var(--muted);font-size:9px}}.issue{{display:grid;grid-template-columns:44px minmax(0,1fr);padding:18px 18px 18px 0;margin-bottom:10px;background:#fff;border:1px solid var(--line);border-left:4px solid var(--slate)}}.issue-high{{border-left-color:var(--red)}}.issue-medium{{border-left-color:var(--amber)}}.issue-low{{border-left-color:var(--green)}}.issue-index{{padding-top:2px;text-align:center;color:#aaa6bb;font-family:var(--serif);font-size:13px}}.issue-meta{{display:flex;flex-wrap:wrap;gap:9px;color:var(--muted);font-size:8px}}.severity{{padding:2px 6px;color:#fff;background:var(--slate);letter-spacing:.06em}}.issue-high .severity{{background:var(--red)}}.issue-medium .severity{{background:var(--amber)}}.issue-low .severity{{background:var(--green)}}.issue h3{{margin:7px 0 4px;font-family:var(--serif);font-size:15px}}.issue-message{{margin:0;color:#4f4b63;font-size:10px}}.issue-evidence,.issue-suggestion{{margin-top:10px;padding:9px 11px;background:#f7f6fb;border-left:2px solid #c8c2e8}}.issue-evidence span,.issue-suggestion span{{display:block;margin-bottom:3px;color:var(--muted);font-size:8px}}.issue-evidence code{{font-family:var(--mono);font-size:9px;word-break:break-word}}.issue-suggestion p{{margin:0;font-size:9px}}.empty{{padding:40px;text-align:center;color:var(--muted);background:#fff;border:1px dashed var(--line)}}.footer{{margin-top:20px;padding-top:14px;color:var(--muted);border-top:1px solid var(--line);font-size:8px;line-height:1.7}}@media(max-width:860px){{.hero-grid,.grid{{grid-template-columns:1fr}}.score-card{{max-width:220px}}.summary{{grid-template-columns:1fr 1fr}}}}@media(max-width:520px){{.page{{padding:12px}}.hero{{padding:22px}}.hero h1{{font-size:24px}}.summary{{grid-template-columns:1fr}}.issue{{grid-template-columns:34px minmax(0,1fr)}}}}
</style>
</head>
<body><main class="page">
<section class="hero"><div class="brand">REPROPROOF · REPRODUCIBILITY AUDIT</div><h1>论文代码可复现性审计报告</h1><p>本报告由 ReproProof 自动生成。结果用于辅助发现可复现性风险，不替代会议或期刊的正式 Artifact Evaluation。</p><div class="hero-grid"><div><div class="meta"><span>仓库：{_e(result.repository)}</span><span>生成时间：{_e(result.generated_at)}</span></div></div><div class="score-card"><strong>{result.score:.1f}<small>/100</small></strong><span>{_e(result.grade)}</span></div></div></section>
<section class="summary"><div><strong>{len(result.issues)}</strong><span>问题总数</span></div><div><strong>{high}</strong><span>高优先级</span></div><div><strong>{medium}</strong><span>中优先级</span></div><div><strong>{low}</strong><span>低优先级</span></div></section>
<section class="grid"><div><div class="card"><h2>维度评分</h2>{dimensions}<div class="stat-list"><div><b>{stats.get('files_scanned',0)}</b><span>扫描文件</span></div><div><b>{stats.get('python_files',0)}</b><span>Python 文件</span></div><div><b>{stats.get('dependency_files',0)}</b><span>依赖清单</span></div><div><b>{'是' if stats.get('paper_loaded') else '否'}</b><span>加载论文</span></div></div></div></div><div><div class="issues-head"><h2>问题与修复建议</h2><span>{_e(result.recommendation)}</span></div>{issue_html}</div></section>
<div class="footer">ReproProof 当前只覆盖 6 条规则：随机种子、依赖锁定、硬编码路径、常见数据泄漏、README 入口和有限论文-代码一致性。规则结果可能存在误报，请结合原文和代码人工确认。</div>
</main></body></html>'''


def write_html(result: AuditResult, output: Path) -> Path:
    output.write_text(render_html(result), encoding="utf-8")
    return output

"""HTML report generation with safe escaping."""

from __future__ import annotations

import html
from datetime import datetime, timedelta, timezone
from typing import Optional

from core.schemas import AnalysisReport, FindingStatus

IST = timezone(timedelta(hours=5, minutes=30))


def _esc(text: Optional[str]) -> str:
    return html.escape(text or "")


def generate_html_report(report: AnalysisReport) -> str:
    generated = datetime.now(IST).strftime("%Y-%m-%d %H:%M %Z")

    findings_rows = []
    for f in report.findings:
        ev = ""
        if f.evidence and f.evidence.document_filename:
            ev = (
                f"{_esc(f.evidence.document_filename)} p.{f.evidence.page_number or '?'}"
                f"<br/><em>{_esc(f.evidence.excerpt)}</em>"
            )
        findings_rows.append(
            f"""
            <tr>
                <td><span class="status-{f.status.value}">{_esc(f.status.value)}</span></td>
                <td>{_esc(f.requirement_id)}</td>
                <td>{_esc(f.requirement_description)}</td>
                <td>{_esc(f.requirement_source.filename)} p.{f.requirement_source.page_number}<br/>
                    <em>{_esc(f.requirement_source.quotation)}</em></td>
                <td>{ev}</td>
                <td>{_esc(f.explanation)}</td>
                <td>{_esc(f.next_action)}</td>
            </tr>
            """
        )

    contra_rows = []
    for c in report.contradictions:
        vals = "<br/>".join(
            f"{_esc(v.field_name)}: {_esc(v.raw_value)} ({_esc(v.source.filename)} p.{v.source.page_number})"
            for v in c.values
        )
        contra_rows.append(
            f"<tr><td>{_esc(c.id)}</td><td>{_esc(c.severity.value)}</td>"
            f"<td>{_esc(c.description)}</td><td>{vals}</td><td>{_esc(c.explanation)}</td></tr>"
        )

    warnings_html = "".join(f"<li>{_esc(w)}</li>" for w in report.warnings)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>PacketProof Submission Readiness Report</title>
<style>
body {{ font-family: Inter, system-ui, sans-serif; margin: 2rem; color: #0f172a; background: #f8fafc; }}
h1 {{ color: #0f172a; }}
.card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
th, td {{ border: 1px solid #e2e8f0; padding: 0.5rem; vertical-align: top; }}
th {{ background: #f1f5f9; text-align: left; }}
.status-verified {{ color: #0f766e; font-weight: 600; }}
.status-missing {{ color: #b91c1c; font-weight: 600; }}
.status-needs_review {{ color: #c2410c; font-weight: 600; }}
.status-not_applicable {{ color: #64748b; font-weight: 600; }}
.disclaimer {{ color: #64748b; font-size: 0.85rem; }}
</style>
</head>
<body>
<h1>PacketProof — Submission Readiness Report</h1>
<p class="disclaimer">Generated {generated}. This report is informational only; it does not guarantee eligibility or acceptance.</p>

<div class="card">
<h2>Summary</h2>
<ul>
<li>Requirements PDF: {_esc(report.requirements_pdf)}</li>
<li>Application documents: {_esc(", ".join(report.application_documents))}</li>
<li>Verified: {report.count_by_status(FindingStatus.VERIFIED)}</li>
<li>Missing: {report.count_by_status(FindingStatus.MISSING)}</li>
<li>Needs review: {report.count_by_status(FindingStatus.NEEDS_REVIEW)}</li>
<li>Contradictions: {len(report.contradictions)}</li>
<li>Analysis duration: {report.analysis_duration_seconds:.1f}s</li>
</ul>
</div>

<div class="card">
<h2>Requirement findings</h2>
<table>
<thead><tr><th>Status</th><th>ID</th><th>Requirement</th><th>Instruction</th><th>Evidence</th><th>Explanation</th><th>Next action</th></tr></thead>
<tbody>
{"".join(findings_rows)}
</tbody>
</table>
</div>

<div class="card">
<h2>Contradictions</h2>
<table>
<thead><tr><th>ID</th><th>Severity</th><th>Field</th><th>Values</th><th>Explanation</th></tr></thead>
<tbody>
{"".join(contra_rows) if contra_rows else "<tr><td colspan='5'>None detected</td></tr>"}
</tbody>
</table>
</div>

<div class="card">
<h2>Warnings</h2>
<ul>{warnings_html or "<li>None</li>"}</ul>
</div>
</body>
</html>
"""

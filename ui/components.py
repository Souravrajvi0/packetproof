"""Reusable Streamlit UI helpers."""

from __future__ import annotations

import html

import streamlit as st

from core.schemas import (
    AnalysisReport,
    Contradiction,
    FindingStatus,
    UploadedDocument,
    VerificationFinding,
)

STATUS_LABELS = {
    FindingStatus.VERIFIED: ("Verified", "pp-badge-verified"),
    FindingStatus.MISSING: ("Missing", "pp-badge-missing"),
    FindingStatus.NEEDS_REVIEW: ("Needs review", "pp-badge-review"),
    FindingStatus.NOT_APPLICABLE: ("Not applicable", "pp-badge-na"),
}


def render_header() -> None:
    st.markdown(
        """
        <div class="pp-header">
            <div class="pp-mark">PP</div>
            <div>
                <h1>PacketProof</h1>
                <div class="pp-tagline">Catch application mistakes before they cost you.</div>
                <div class="pp-pills">
                    <span class="pp-pill">Gemma 3 4B</span>
                    <span class="pp-pill">Evidence-backed</span>
                    <span class="pp-pill">Ollama or OpenRouter</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(active: int) -> None:
    steps = [
        (1, "Requirements"),
        (2, "Documents"),
        (3, "Analyze"),
        (4, "Review"),
        (5, "Export"),
    ]
    cards = []
    for n, title in steps:
        cls = "pp-step active" if n == active else "pp-step"
        cards.append(
            f'<div class="{cls}"><span class="n">Step {n}</span>'
            f'<span class="t">{title}</span></div>'
        )
    st.markdown(f'<div class="pp-stepper">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_examples() -> None:
    st.markdown(
        """
        <div class="pp-examples">
          <div class="pp-ex">
            <h3>What you can add</h3>
            <ul>
              <li>Scholarship or visa instruction PDF</li>
              <li>Photo of a printed checklist</li>
              <li>Paste rules from a website</li>
              <li>Application form, ID, transcript, letter</li>
            </ul>
          </div>
          <div class="pp-ex">
            <h3>What PacketProof checks</h3>
            <ul>
              <li>Missing documents (e.g. no transcript)</li>
              <li>GPA or score below a stated minimum</li>
              <li>Dates that conflict (form vs resume)</li>
              <li>Unsigned declarations, stale letters</li>
            </ul>
          </div>
          <div class="pp-ex">
            <h3>Example packets</h3>
            <ul>
              <li>University / scholarship applications</li>
              <li>Internships and job packets</li>
              <li>Grant or visa supporting files</li>
              <li>Try the built-in Meridian demo below</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_document_card(doc: UploadedDocument) -> None:
    readable = sum(1 for p in doc.pages if p.is_readable)
    status = "Extracted" if readable else "Unreadable"
    badge = "pp-badge-ok" if readable else "pp-badge-warn"
    st.markdown(
        f"""
        <div class="pp-doc-card">
            <div class="pp-doc-name">{html.escape(doc.filename)}</div>
            <span class="pp-muted">{doc.page_count} pages · {readable} readable</span>
            &nbsp;<span class="pp-badge {badge}">{status}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if doc.extraction_warnings:
        for w in doc.extraction_warnings[:3]:
            st.warning(w)


def render_overview_metrics(report: AnalysisReport) -> None:
    cols = st.columns(4)
    metrics = [
        ("Verified", report.count_by_status(FindingStatus.VERIFIED), "pp-metric-verified"),
        ("Missing", report.count_by_status(FindingStatus.MISSING), "pp-metric-missing"),
        ("Needs review", report.count_by_status(FindingStatus.NEEDS_REVIEW), "pp-metric-review"),
        ("Contradictions", len(report.contradictions), "pp-metric-neutral"),
    ]
    for col, (label, value, css) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="pp-card {css}">
                    <div class="pp-muted">{label}</div>
                    <div style="font-size:2rem;font-weight:700;color:#0f172a;letter-spacing:-0.04em;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.caption(
        f"Applicable requirements: {report.applicable_count} · "
        f"Extracted: {len(report.requirements)} · "
        f"Time: {report.analysis_duration_seconds:.1f}s"
    )


def render_document_coverage(report: AnalysisReport) -> None:
    if not report.document_coverage:
        return
    st.markdown("**Document coverage**")
    cols = st.columns(min(3, max(1, len(report.document_coverage))))
    items = sorted(report.document_coverage.items())
    for i, (filename, count) in enumerate(items):
        with cols[i % len(cols)]:
            st.markdown(
                f'<div class="pp-doc-card"><div class="pp-doc-name">{html.escape(filename)}</div>'
                f'<span class="pp-muted">{count} match(es)</span></div>',
                unsafe_allow_html=True,
            )


def render_evidence_inspector(findings: list[VerificationFinding]) -> None:
    if not findings:
        st.markdown(
            '<div class="pp-empty">Run analysis to inspect requirement quotations and matching evidence.</div>',
            unsafe_allow_html=True,
        )
        return
    options = {
        f"{f.requirement_id}: {f.requirement_description[:60]}": f for f in findings
    }
    choice = st.selectbox("Select a requirement", list(options.keys()))
    finding = options[choice]
    label, badge_class = STATUS_LABELS.get(finding.status, ("Unknown", "pp-badge-na"))
    st.markdown(
        f'<span class="pp-badge {badge_class}">{label}</span>',
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        st.markdown("**Instruction citation**")
        st.markdown(
            f'<div class="pp-quote">{html.escape(finding.requirement_source.quotation)}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            f"{finding.requirement_source.filename} · page {finding.requirement_source.page_number}"
        )
    with right:
        st.markdown("**Matching evidence**")
        if finding.evidence and (finding.evidence.document_filename or finding.evidence.excerpt):
            st.markdown(
                f'<div class="pp-quote">{html.escape(finding.evidence.excerpt or "(no excerpt)")}</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f"{finding.evidence.document_filename or '—'} · page {finding.evidence.page_number or '—'}"
            )
            st.write(finding.evidence.explanation)
        else:
            st.markdown(
                '<div class="pp-empty">Evidence not found in uploaded documents.</div>',
                unsafe_allow_html=True,
            )
    st.markdown("**Validated explanation**")
    st.write(finding.explanation)
    if finding.validation_notes:
        st.info("Verifier notes: " + "; ".join(finding.validation_notes))


def render_finding_row(finding: VerificationFinding, key: str) -> None:
    label, badge_class = STATUS_LABELS.get(finding.status, ("Unknown", "pp-badge-na"))
    title = f"{finding.requirement_id}  ·  {finding.requirement_description[:90]}"
    with st.expander(title, expanded=False):
        st.markdown(
            f'<span class="pp-badge {badge_class}">{label}</span>',
            unsafe_allow_html=True,
        )
        st.write(finding.explanation)
        st.markdown("**Instruction source**")
        st.markdown(
            f'<div class="pp-quote">{html.escape(finding.requirement_source.quotation)}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            f"{finding.requirement_source.filename} · page {finding.requirement_source.page_number}"
        )
        if finding.evidence and finding.evidence.document_filename:
            st.markdown("**Evidence**")
            st.markdown(
                f'<div class="pp-quote">{html.escape(finding.evidence.excerpt or "")}</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f"{finding.evidence.document_filename} · page {finding.evidence.page_number or '?'}"
            )
        st.markdown(f"**Next action:** {finding.next_action}")
        if finding.validation_notes:
            st.info("Validation: " + "; ".join(finding.validation_notes))


def render_contradictions(contradictions: list[Contradiction]) -> None:
    if not contradictions:
        st.markdown(
            '<div class="pp-empty">No cross-document contradictions were detected. '
            "This does not prove authenticity.</div>",
            unsafe_allow_html=True,
        )
        return
    for c in contradictions:
        with st.expander(f"{c.id}: {c.description} ({c.severity.value})"):
            st.write(c.explanation)
            if c.may_be_benign:
                st.caption("This difference may have a legitimate explanation.")
            for v in c.values:
                st.markdown(
                    f"- **{html.escape(v.field_name)}** = {html.escape(v.raw_value)} "
                    f"({html.escape(v.source.filename)}, p.{v.source.page_number})"
                )


def render_action_plan(findings: list[VerificationFinding]) -> None:
    priority = [
        f for f in findings if f.status in (FindingStatus.MISSING, FindingStatus.NEEDS_REVIEW)
    ]
    if not priority:
        st.markdown(
            '<div class="pp-empty">No urgent actions identified. Review verified items for extra confidence.</div>',
            unsafe_allow_html=True,
        )
        return
    for i, f in enumerate(priority, 1):
        st.checkbox(
            f"{i}. [{f.status.value.replace('_', ' ')}] {f.requirement_description} — {f.next_action}",
            key=f"action_{f.requirement_id}",
        )

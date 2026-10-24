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
            <h1>PacketProof</h1>
            <div class="pp-tagline">Catch application mistakes before they cost you.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_document_card(doc: UploadedDocument) -> None:
    readable = sum(1 for p in doc.pages if p.is_readable)
    st.markdown(
        f"""
        <div class="pp-doc-card">
            <strong>{html.escape(doc.filename)}</strong><br/>
            <span class="pp-muted">{doc.page_count} pages · {readable} with extractable text</span>
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
                    <div style="font-size:2rem;font-weight:700;color:#0f172a;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.caption(
        f"Applicable requirements: {report.applicable_count} · "
        f"Total extracted: {len(report.requirements)} · "
        f"Analysis time: {report.analysis_duration_seconds:.1f}s"
    )


def render_document_coverage(report: AnalysisReport) -> None:
    if not report.document_coverage:
        st.caption("No document coverage data yet.")
        return
    st.markdown("**Document coverage** (requirements with supported/partial evidence per file)")
    for filename, count in sorted(report.document_coverage.items()):
        st.markdown(
            f'<div class="pp-doc-card"><strong>{html.escape(filename)}</strong> — '
            f'<span class="pp-muted">{count} requirement match(es)</span></div>',
            unsafe_allow_html=True,
        )


def render_evidence_inspector(findings: list[VerificationFinding]) -> None:
    if not findings:
        st.info("Run analysis to inspect evidence.")
        return
    options = {
        f"{f.requirement_id}: {f.requirement_description[:60]}": f for f in findings
    }
    choice = st.selectbox("Select a requirement", list(options.keys()))
    finding = options[choice]
    label, badge_class = STATUS_LABELS.get(finding.status, ("Unknown", "pp-badge-na"))
    st.markdown(f'<span class="pp-badge {badge_class}">{label}</span>', unsafe_allow_html=True)
    st.markdown("#### Instruction citation")
    st.code(
        f"File: {finding.requirement_source.filename}\n"
        f"Page: {finding.requirement_source.page_number}\n\n"
        f"{finding.requirement_source.quotation}"
    )
    st.markdown("#### Matching evidence")
    if finding.evidence and (finding.evidence.document_filename or finding.evidence.excerpt):
        st.code(
            f"File: {finding.evidence.document_filename or '—'}\n"
            f"Page: {finding.evidence.page_number or '—'}\n\n"
            f"{finding.evidence.excerpt or '(no excerpt)'}\n\n"
            f"Provisional: {finding.evidence.provisional_status.value}"
        )
        st.write(finding.evidence.explanation)
    else:
        st.warning("No supporting evidence located in uploaded documents.")
    st.markdown("#### Validated explanation")
    st.write(finding.explanation)
    if finding.validation_notes:
        st.info("Verifier notes: " + "; ".join(finding.validation_notes))


def render_finding_row(finding: VerificationFinding, key: str) -> None:
    label, badge_class = STATUS_LABELS.get(finding.status, ("Unknown", "pp-badge-na"))
    with st.expander(f"{finding.requirement_id}: {finding.requirement_description[:80]}", expanded=False):
        st.markdown(
            f'<span class="pp-badge {badge_class}">{label}</span>',
            unsafe_allow_html=True,
        )
        st.write(finding.explanation)
        st.markdown("**Instruction source**")
        st.code(
            f"{finding.requirement_source.filename} · page {finding.requirement_source.page_number}\n"
            f'"{finding.requirement_source.quotation}"'
        )
        if finding.evidence and finding.evidence.document_filename:
            st.markdown("**Evidence**")
            st.code(
                f"{finding.evidence.document_filename} · page {finding.evidence.page_number or '?'}\n"
                f'"{finding.evidence.excerpt or ""}"'
            )
        st.markdown(f"**Next action:** {finding.next_action}")
        if finding.validation_notes:
            st.info("Validation: " + "; ".join(finding.validation_notes))


def render_contradictions(contradictions: list[Contradiction]) -> None:
    if not contradictions:
        st.success("No cross-document contradictions were detected.")
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
        st.write("No urgent actions identified. Review verified items if you want extra confidence.")
        return
    for i, f in enumerate(priority, 1):
        st.checkbox(
            f"{i}. [{f.status.value}] {f.requirement_description} — {f.next_action}",
            key=f"action_{f.requirement_id}",
        )

"""PacketProof Streamlit application."""

from __future__ import annotations

import streamlit as st

from core.llm_client import DEFAULT_MODEL, OllamaClient
from core.pdf_processor import extract_pdf_from_bytes
from core.pipeline import run_analysis
from core.schemas import LLMError
from reports.html_report import generate_html_report
from ui.components import (
    render_action_plan,
    render_contradictions,
    render_document_card,
    render_finding_row,
    render_header,
    render_overview_metrics,
)
from ui.styles import CUSTOM_CSS

st.set_page_config(
    page_title="PacketProof",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_session() -> None:
    defaults = {
        "requirements_file": None,
        "requirements_doc": None,
        "application_files": [],
        "application_docs": [],
        "report": None,
        "analysis_stage": "",
        "analysis_progress": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def clear_session() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()


def sidebar() -> None:
    with st.sidebar:
        st.markdown("### Settings")
        ollama_url = st.text_input("Ollama URL", value="http://127.0.0.1:11434")
        model = st.text_input("Model", value=DEFAULT_MODEL)
        st.session_state["ollama_url"] = ollama_url
        st.session_state["ollama_model"] = model

        client = OllamaClient(base_url=ollama_url, model=model)
        if client.is_available():
            st.success("Ollama connected")
        else:
            st.warning("Ollama not reachable — start Ollama and pull gemma3:4b")

        st.markdown("---")
        if st.button("Clear session", type="secondary"):
            clear_session()
            st.rerun()

        st.markdown(
            """
            **Privacy:** Documents are processed in memory on this machine.
            PacketProof does not send your PDFs to external AI APIs.
            """
        )


def step_requirements() -> None:
    st.markdown('<div class="pp-step-label">Step 1 — Upload requirements</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Application instructions (PDF)",
        type=["pdf"],
        key="req_uploader",
    )
    if uploaded:
        data = uploaded.getvalue()
        try:
            doc = extract_pdf_from_bytes(uploaded.name, data)
            st.session_state["requirements_file"] = (uploaded.name, data)
            st.session_state["requirements_doc"] = doc
            render_document_card(doc)
            excerpt = doc.full_text[:1500]
            if excerpt.strip():
                st.markdown("**Extracted excerpt**")
                st.text_area("Requirements preview", excerpt, height=200, disabled=True)
            else:
                st.error("No extractable text found in the requirements PDF.")
        except Exception as exc:
            st.error(str(exc))


def step_application() -> None:
    st.markdown('<div class="pp-step-label">Step 2 — Upload application documents</div>', unsafe_allow_html=True)
    uploads = st.file_uploader(
        "Application & supporting PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key="app_uploader",
    )
    if uploads:
        files: list[tuple[str, bytes]] = []
        docs = []
        for f in uploads:
            data = f.getvalue()
            files.append((f.name, data))
            try:
                docs.append(extract_pdf_from_bytes(f.name, data))
            except Exception as exc:
                st.error(f"{f.name}: {exc}")
        st.session_state["application_files"] = files
        st.session_state["application_docs"] = docs
        for doc in docs:
            render_document_card(doc)


def step_analyze() -> None:
    st.markdown('<div class="pp-step-label">Step 3 — Analyze</div>', unsafe_allow_html=True)
    ready = (
        st.session_state.get("requirements_file")
        and st.session_state.get("application_files")
    )
    if not ready:
        st.info("Upload requirements and at least one application PDF to continue.")
        return

    if st.button("Analyze Application", type="primary", use_container_width=True):
        progress_bar = st.progress(0.0)
        status = st.empty()

        def on_progress(stage: str, fraction: float) -> None:
            st.session_state["analysis_stage"] = stage
            st.session_state["analysis_progress"] = fraction
            progress_bar.progress(min(1.0, max(0.0, fraction)))
            status.markdown(f"**{stage}**")

        client = OllamaClient(
            base_url=st.session_state.get("ollama_url", "http://127.0.0.1:11434"),
            model=st.session_state.get("ollama_model", DEFAULT_MODEL),
        )
        try:
            report = run_analysis(
                st.session_state["requirements_file"],
                st.session_state["application_files"],
                client=client,
                progress=on_progress,
            )
            st.session_state["report"] = report
            st.success("Analysis complete.")
        except LLMError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")


def step_results() -> None:
    report = st.session_state.get("report")
    if not report:
        return

    st.markdown('<div class="pp-step-label">Step 4 — Review results</div>', unsafe_allow_html=True)
    render_overview_metrics(report)

    if report.warnings:
        with st.expander("Extraction warnings"):
            for w in report.warnings:
                st.warning(w)

    tab_checklist, tab_issues, tab_contra, tab_plan = st.tabs(
        ["Checklist", "Issue explorer", "Contradictions", "Action plan"]
    )

    with tab_checklist:
        for f in report.findings:
            render_finding_row(f, f.requirement_id)

    with tab_issues:
        statuses = sorted({f.status.value for f in report.findings})
        selected = st.multiselect("Filter by status", statuses, default=statuses)
        for f in report.findings:
            if f.status.value in selected:
                render_finding_row(f, f"filter_{f.requirement_id}")

    with tab_contra:
        render_contradictions(report.contradictions)

    with tab_plan:
        render_action_plan(report.findings)

    st.markdown('<div class="pp-step-label">Step 5 — Export</div>', unsafe_allow_html=True)
    html_content = generate_html_report(report)
    st.download_button(
        "Download HTML report",
        data=html_content,
        file_name="packetproof_report.html",
        mime="text/html",
        use_container_width=True,
    )


def main() -> None:
    init_session()
    sidebar()
    render_header()
    step_requirements()
    st.markdown("---")
    step_application()
    st.markdown("---")
    step_analyze()
    st.markdown("---")
    step_results()
    st.markdown(
        '<div class="pp-footer">PacketProof · Local open-weight AI · Not legal advice</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

"""PacketProof Streamlit application."""

from __future__ import annotations

import streamlit as st

import os

from core.llm_client import DEFAULT_MODEL
from core.llm_factory import create_llm_client
from core.openrouter_client import DEFAULT_OPENROUTER_MODEL
from core.pdf_processor import extract_pdf_from_bytes
from core.pipeline import run_analysis
from core.schemas import LLMError
from reports.html_report import generate_html_report
from ui.components import (
    render_action_plan,
    render_contradictions,
    render_document_card,
    render_document_coverage,
    render_evidence_inspector,
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


def _secret_openrouter_key() -> str:
    try:
        return str(st.secrets.get("OPENROUTER_API_KEY", "")).strip()
    except Exception:
        return ""


def sidebar() -> None:
    with st.sidebar:
        st.markdown("### Inference")
        default_provider = (
            "openrouter"
            if os.environ.get("OPENROUTER_API_KEY") or _secret_openrouter_key()
            else "ollama"
        )
        provider = st.radio(
            "Provider",
            options=["openrouter", "ollama"],
            format_func=lambda x: "OpenRouter (Gemma 3 4B cloud)" if x == "openrouter" else "Ollama (local)",
            index=0 if default_provider == "openrouter" else 1,
        )
        st.session_state["llm_provider"] = provider

        if provider == "openrouter":
            env_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
            default_key = env_key or _secret_openrouter_key()
            api_key = st.text_input(
                "OpenRouter API key",
                value=default_key,
                type="password",
                help="Set OPENROUTER_API_KEY env var to avoid pasting here.",
            )
            or_model = st.text_input("OpenRouter model", value=DEFAULT_OPENROUTER_MODEL)
            st.session_state["openrouter_api_key"] = api_key
            st.session_state["openrouter_model"] = or_model
            if api_key:
                st.success("OpenRouter key set")
            else:
                st.warning("Add your OpenRouter API key")
            st.caption("PDF text is sent to OpenRouter for inference.")
        else:
            ollama_url = st.text_input("Ollama URL", value="http://127.0.0.1:11434")
            model = st.text_input("Ollama model", value=DEFAULT_MODEL)
            st.session_state["ollama_url"] = ollama_url
            st.session_state["ollama_model"] = model
            probe = create_llm_client(
                "ollama", ollama_url=ollama_url, ollama_model=model, timeout=5.0
            )
            if probe.is_available():
                st.success("Ollama connected")
            else:
                st.warning("Ollama not reachable — run `ollama pull gemma3:4b`")
            st.caption("Documents stay on this machine.")

        st.markdown("---")
        if st.button("Clear session", type="secondary"):
            clear_session()
            st.rerun()


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

        provider = st.session_state.get("llm_provider", "ollama")
        if provider == "openrouter":
            client = create_llm_client(
                "openrouter",
                openrouter_api_key=st.session_state.get("openrouter_api_key", ""),
                openrouter_model=st.session_state.get(
                    "openrouter_model", DEFAULT_OPENROUTER_MODEL
                ),
                timeout=600.0,
            )
        else:
            client = create_llm_client(
                "ollama",
                ollama_url=st.session_state.get("ollama_url", "http://127.0.0.1:11434"),
                ollama_model=st.session_state.get("ollama_model", DEFAULT_MODEL),
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
    render_document_coverage(report)

    if report.warnings:
        with st.expander("Extraction warnings"):
            for w in report.warnings:
                st.warning(w)

    tab_checklist, tab_issues, tab_evidence, tab_contra, tab_plan = st.tabs(
        ["Checklist", "Issue explorer", "Evidence inspector", "Contradictions", "Action plan"]
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

    with tab_evidence:
        render_evidence_inspector(report.findings)

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

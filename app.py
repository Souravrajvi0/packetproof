"""PacketProof Streamlit application."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from core.env_loader import load_dotenv

load_dotenv()

from core.llm_client import DEFAULT_MODEL
from core.llm_factory import create_llm_client
from core.openrouter_client import DEFAULT_OPENROUTER_MODEL
from core.ingest import document_from_text, ingest_bytes
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
    render_examples,
    render_overview_metrics,
    render_stepper,
)
from ui.styles import CUSTOM_CSS

st.set_page_config(
    page_title="PacketProof",
    page_icon="PP",
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


def _default_provider_index() -> int:
    env_mode = os.environ.get("PACKETPROOF_INFERENCE", "ollama").strip().lower()
    if env_mode == "openrouter" and (
        os.environ.get("OPENROUTER_API_KEY") or _secret_openrouter_key()
    ):
        return 0
    return 1


def _active_step() -> int:
    if st.session_state.get("report"):
        return 4
    if st.session_state.get("requirements_file") and st.session_state.get("application_files"):
        return 3
    if st.session_state.get("requirements_file"):
        return 2
    return 1


def sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="pp-sidebar-brand">PacketProof</div>', unsafe_allow_html=True)
        st.caption("Gemma 3 4B · evidence-backed review")
        st.markdown("---")
        st.markdown("**Inference**")
        provider = st.radio(
            "Provider",
            options=["openrouter", "ollama"],
            index=_default_provider_index(),
            format_func=lambda x: (
                "OpenRouter — hosted (fast)"
                if x == "openrouter"
                else "Ollama — local (private)"
            ),
            key="provider_radio",
            label_visibility="collapsed",
        )
        st.session_state["llm_provider"] = provider

        if provider == "openrouter":
            env_key = os.environ.get("OPENROUTER_API_KEY", "").strip() or _secret_openrouter_key()
            api_key = st.text_input(
                "OpenRouter API key",
                value=env_key,
                type="password",
                help="Or set OPENROUTER_API_KEY in .env",
            )
            or_model = st.text_input("Model", value=DEFAULT_OPENROUTER_MODEL)
            st.session_state["openrouter_api_key"] = api_key
            st.session_state["openrouter_model"] = or_model
            if api_key:
                st.success("OpenRouter ready")
            else:
                st.warning("Add API key in .env")
            st.caption("Cloud: extracted PDF text is sent to OpenRouter.")
        else:
            ollama_url = st.text_input("Ollama URL", value="http://127.0.0.1:11434")
            model = st.text_input("Model", value=DEFAULT_MODEL)
            st.session_state["ollama_url"] = ollama_url
            st.session_state["ollama_model"] = model
            probe = create_llm_client(
                "ollama", ollama_url=ollama_url, ollama_model=model, timeout=5.0
            )
            if probe.is_available():
                st.success("Ollama connected")
            else:
                st.warning("Run `ollama pull gemma3:4b`")
            st.caption("Local: PDF text stays on this machine.")

        st.markdown("---")
        if st.button("Clear session", type="secondary", use_container_width=True):
            clear_session()
            st.rerun()
        st.caption("Not legal advice. Does not prove authenticity or eligibility.")


ACCEPTED_TYPES = ["pdf", "txt", "md", "png", "jpg", "jpeg", "webp", "gif"]
DEMO_DIR = Path(__file__).resolve().parent / "demo" / "samples"
EXAMPLE_REQUIREMENTS = """Meridian Future Scholars Program — example rules

1. Submit a completed application form (signed where indicated).
2. An official academic transcript is required.
3. Provide a government-issued photo ID copy.
4. One faculty recommendation letter dated within the last 6 months.
5. Personal statement, maximum two pages.
6. Minimum cumulative GPA of 3.0 on a 4.0 scale.
7. The applicant declaration must be signed and dated.
"""


def _active_client():
    provider = st.session_state.get("llm_provider", "ollama")
    if provider == "openrouter":
        return create_llm_client(
            "openrouter",
            openrouter_api_key=st.session_state.get("openrouter_api_key", ""),
            openrouter_model=st.session_state.get(
                "openrouter_model", DEFAULT_OPENROUTER_MODEL
            ),
            timeout=600.0,
        )
    return create_llm_client(
        "ollama",
        ollama_url=st.session_state.get("ollama_url", "http://127.0.0.1:11434"),
        ollama_model=st.session_state.get("ollama_model", DEFAULT_MODEL),
    )


def _demo_loader() -> None:
    with st.expander("Try a ready-made example (Meridian Scholars, fictional)"):
        st.markdown(
            "Loads a sample **requirements PDF** plus application form, ID, "
            "recommendation letter, resume, and personal statement. "
            "Planted issues: missing transcript, GPA 2.7 vs 3.0, date mismatch, unsigned form."
        )
        if st.button("Load demo packet", type="secondary"):
            req = DEMO_DIR / "meridian_requirements_2026.pdf"
            if not req.exists():
                st.error("Demo files missing. Run `python3 demo/generate_samples.py`.")
                return
            req_bytes = req.read_bytes()
            st.session_state["requirements_file"] = (req.name, req_bytes)
            st.session_state["requirements_doc"] = ingest_bytes(req.name, req_bytes)
            apps = []
            docs = []
            for name in [
                "application_form.pdf",
                "resume.pdf",
                "recommendation_letter.pdf",
                "photo_id_copy.pdf",
                "personal_statement.pdf",
            ]:
                path = DEMO_DIR / name
                if path.exists():
                    data = path.read_bytes()
                    apps.append((name, data))
                    docs.append(ingest_bytes(name, data))
            st.session_state["application_files"] = apps
            st.session_state["application_docs"] = docs
            st.success("Demo packet loaded. Click **Analyze application** below.")
            st.rerun()
        if st.session_state.get("requirements_file") and st.session_state.get("application_docs"):
            st.caption("Current packet is loaded. You can still replace files in the upload boxes.")


def _preview_doc(doc) -> None:
    render_document_card(doc)
    excerpt = doc.full_text[:1200]
    if excerpt.strip():
        with st.expander("Preview extracted text", expanded=False):
            st.text(excerpt)
    elif doc.extraction_warnings:
        st.warning(doc.extraction_warnings[0])


def step_requirements() -> None:
    st.markdown('<div class="pp-step-label">1 · Requirements</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pp-help">PDF, photo, text file, or paste the instructions.</div>',
        unsafe_allow_html=True,
    )
    tab_file, tab_paste = st.tabs(["Upload file", "Paste text"])
    with tab_file:
        uploaded = st.file_uploader(
            "Drop PDF, image, or .txt",
            type=ACCEPTED_TYPES,
            key="req_uploader",
        )
        if uploaded:
            data = uploaded.getvalue()
            try:
                client = _active_client()
                doc = ingest_bytes(uploaded.name, data, vision_client=client)
                st.session_state["requirements_file"] = (uploaded.name, data)
                st.session_state["requirements_doc"] = doc
                _preview_doc(doc)
            except Exception as exc:
                st.error(str(exc))
        elif not st.session_state.get("requirements_file"):
            st.markdown(
                '<div class="pp-empty">Examples: scholarship_rules.pdf, a phone photo of the '
                "checklist, or eligibility.txt from the program website.</div>",
                unsafe_allow_html=True,
            )
    with tab_paste:
        if st.button("Insert example scholarship rules", key="insert_example_req"):
            st.session_state["req_paste"] = EXAMPLE_REQUIREMENTS
            st.rerun()
        pasted = st.text_area(
            "Paste eligibility or instruction text",
            height=180,
            placeholder="Example: Applicants must submit a transcript and have a GPA of 3.0…",
            key="req_paste",
        )
        if st.button("Use pasted text", key="use_paste_req"):
            if not pasted.strip():
                st.error("Paste some instruction text first.")
            else:
                doc = document_from_text("pasted_requirements.txt", pasted)
                st.session_state["requirements_file"] = (
                    "pasted_requirements.txt",
                    pasted.encode("utf-8"),
                )
                st.session_state["requirements_doc"] = doc
                _preview_doc(doc)


def step_application() -> None:
    st.markdown('<div class="pp-step-label">2 · Application documents</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pp-help">PDFs, photos of ID/letters, or text files. Multiple files OK.</div>',
        unsafe_allow_html=True,
    )
    uploads = st.file_uploader(
        "Drop PDFs, images, or text files",
        type=ACCEPTED_TYPES,
        accept_multiple_files=True,
        key="app_uploader",
    )
    if uploads:
        files: list[tuple[str, bytes]] = []
        docs = []
        client = _active_client()
        for f in uploads:
            data = f.getvalue()
            files.append((f.name, data))
            try:
                docs.append(ingest_bytes(f.name, data, vision_client=client))
            except Exception as exc:
                st.error(f"{f.name}: {exc}")
        st.session_state["application_files"] = files
        st.session_state["application_docs"] = docs
        for doc in docs:
            render_document_card(doc)
    else:
        st.markdown(
            '<div class="pp-empty">Examples: application_form.pdf, photo_id.jpg, '
            "recommendation_letter.pdf, resume.pdf.</div>",
            unsafe_allow_html=True,
        )


def step_analyze() -> None:
    st.markdown('<div class="pp-step-label">3 · Analyze with Gemma</div>', unsafe_allow_html=True)
    ready = (
        st.session_state.get("requirements_file")
        and st.session_state.get("application_files")
    )
    if not ready:
        st.markdown(
            '<div class="pp-empty">Add requirements (file or paste) and at least one supporting document to analyze.</div>',
            unsafe_allow_html=True,
        )
        return

    n_app = len(st.session_state.get("application_files") or [])
    st.caption(f"Ready: 1 requirements file · {n_app} application file(s)")

    if st.button("Analyze application", type="primary", use_container_width=True):
        progress_bar = st.progress(0.0)
        status = st.empty()

        def on_progress(stage: str, fraction: float) -> None:
            st.session_state["analysis_stage"] = stage
            st.session_state["analysis_progress"] = fraction
            progress_bar.progress(min(1.0, max(0.0, fraction)))
            status.markdown(f"**{stage}**")

        client = _active_client()
        try:
            report = run_analysis(
                st.session_state["requirements_file"],
                st.session_state["application_files"],
                client=client,
                progress=on_progress,
            )
            st.session_state["report"] = report
            st.success("Analysis complete. Scroll to review evidence-backed findings.")
        except LLMError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")


def step_results() -> None:
    report = st.session_state.get("report")
    if not report:
        return

    st.markdown('<div class="pp-step-label">4 · Readiness dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pp-help">This is not an approval or eligibility verdict.</div>',
        unsafe_allow_html=True,
    )
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

    st.markdown('<div class="pp-step-label">5 · Export</div>', unsafe_allow_html=True)
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
    render_stepper(_active_step())
    render_examples()
    _demo_loader()
    col_a, col_b = st.columns(2)
    with col_a:
        step_requirements()
    with col_b:
        step_application()
    st.markdown("")
    step_analyze()
    step_results()
    st.markdown(
        '<div class="pp-footer">PacketProof · Gemma 3 4B · Evidence-backed review · Not legal advice</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

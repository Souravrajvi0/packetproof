"""End-to-end analysis pipeline."""

from __future__ import annotations

import time
from typing import Callable, Optional

from core.applicability import assess_applicability
from core.contradictions import detect_contradictions
from core.evidence import match_all_evidence
from core.llm_factory import LLMClient, create_llm_client, resolve_provider
from core.ingest import ingest_bytes
from core.requirements import extract_requirements
from core.schemas import AnalysisReport, LLMError, UploadedDocument
from core.verifier import build_findings, document_coverage

ProgressCallback = Callable[[str, float], None]


def _noop_progress(stage: str, fraction: float) -> None:
    pass


def run_analysis(
    requirements_bytes: tuple[str, bytes],
    application_files: list[tuple[str, bytes]],
    client: Optional[LLMClient] = None,
    progress: ProgressCallback = _noop_progress,
    json_loader: Optional[Callable] = None,
    skip_contradictions: bool = False,
) -> AnalysisReport:
    start = time.perf_counter()
    warnings: list[str] = []

    progress("Reading documents", 0.05)
    llm = client or create_llm_client(resolve_provider())
    req_name, req_data = requirements_bytes
    instructions = ingest_bytes(req_name, req_data, vision_client=llm)
    app_docs: list[UploadedDocument] = []
    for fname, data in application_files:
        try:
            app_docs.append(ingest_bytes(fname, data, vision_client=llm))
        except Exception as exc:
            warnings.append(f"Skipped {fname}: {exc}")

    if not app_docs:
        raise ValueError("No valid application documents were uploaded.")

    for doc in [instructions] + app_docs:
        warnings.extend(doc.extraction_warnings)

    if json_loader is None and not llm.is_available():
        raise LLMError(
            "No LLM available. Use OpenRouter (API key) or start Ollama with `ollama pull gemma3:4b`."
        )

    progress("Extracting requirements", 0.2)
    try:
        requirements = extract_requirements(instructions, llm, json_loader=json_loader)
    except LLMError as exc:
        warnings.append(f"Requirement extraction had invalid JSON: {exc}")
        requirements = []
    if not requirements:
        warnings.append("No requirements were extracted; review the instruction text.")

    progress("Assessing conditional requirements", 0.35)
    applicability = assess_applicability(requirements, app_docs, llm, json_loader=json_loader)
    applicable_requirements = [
        r for r in requirements if applicability.get(r.id, (True, ""))[0]
    ]

    progress("Matching supporting evidence", 0.45)

    def match_progress(msg: str) -> None:
        progress(msg, 0.5)

    matches = match_all_evidence(
        applicable_requirements,
        app_docs,
        llm,
        progress_callback=match_progress,
        json_loader=json_loader,
    )

    progress("Checking inconsistencies", 0.7)
    contradictions = []
    if not skip_contradictions:
        try:
            contradictions = detect_contradictions(app_docs, llm, json_loader=json_loader)
        except LLMError as exc:
            warnings.append(f"Contradiction detection skipped: {exc}")

    progress("Generating report", 0.85)
    findings = build_findings(
        requirements, matches, instructions, app_docs, applicability=applicability
    )
    coverage = document_coverage(app_docs, matches)

    duration = time.perf_counter() - start
    progress("Complete", 1.0)

    return AnalysisReport(
        requirements_pdf=instructions.filename,
        application_documents=[d.filename for d in app_docs],
        requirements=requirements,
        provisional_matches=matches,
        contradictions=contradictions,
        findings=findings,
        document_coverage=coverage,
        warnings=warnings,
        analysis_duration_seconds=duration,
    )

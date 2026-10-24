"""End-to-end analysis pipeline."""

from __future__ import annotations

import time
from typing import Callable, Optional

from core.applicability import assess_applicability
from core.contradictions import detect_contradictions
from core.evidence import match_all_evidence
from core.llm_client import OllamaClient
from core.pdf_processor import extract_pdf_from_bytes
from core.requirements import extract_requirements
from core.schemas import AnalysisReport, LLMError, UploadedDocument
from core.verifier import build_findings, document_coverage

ProgressCallback = Callable[[str, float], None]


def _noop_progress(stage: str, fraction: float) -> None:
    pass


def run_analysis(
    requirements_bytes: tuple[str, bytes],
    application_files: list[tuple[str, bytes]],
    client: Optional[OllamaClient] = None,
    progress: ProgressCallback = _noop_progress,
    json_loader: Optional[Callable] = None,
    skip_contradictions: bool = False,
) -> AnalysisReport:
    start = time.perf_counter()
    warnings: list[str] = []

    progress("Reading documents", 0.05)
    req_name, req_data = requirements_bytes
    instructions = extract_pdf_from_bytes(req_name, req_data)
    app_docs: list[UploadedDocument] = []
    for fname, data in application_files:
        try:
            app_docs.append(extract_pdf_from_bytes(fname, data))
        except Exception as exc:
            warnings.append(f"Skipped {fname}: {exc}")

    if not app_docs:
        raise ValueError("No valid application documents were uploaded.")

    for doc in [instructions] + app_docs:
        warnings.extend(doc.extraction_warnings)

    llm = client or OllamaClient()
    if json_loader is None and not llm.is_available():
        raise LLMError(
            "Ollama is not reachable. Install Ollama, run `ollama pull gemma3:4b`, and start the service."
        )

    progress("Extracting requirements", 0.2)
    requirements = extract_requirements(instructions, llm, json_loader=json_loader)
    if not requirements:
        warnings.append("No requirements were extracted; review the instructions PDF.")

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

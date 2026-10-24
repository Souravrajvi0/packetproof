#!/usr/bin/env python3
"""Compare PacketProof findings against the demo answer key."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import os

from core.llm_factory import create_llm_client, resolve_provider
from core.pipeline import run_analysis
from core.schemas import FindingStatus, LLMError

SAMPLES = ROOT / "demo" / "samples"
ANSWER_KEY = ROOT / "demo" / "answer_key.json"


def load_demo_files() -> tuple[tuple[str, bytes], list[tuple[str, bytes]]]:
    req = SAMPLES / "meridian_requirements_2026.pdf"
    if not req.exists():
        raise FileNotFoundError(
            "Demo samples missing. Run: python3 demo/generate_samples.py"
        )
    app_names = [
        "application_form.pdf",
        "resume.pdf",
        "recommendation_letter.pdf",
        "photo_id_copy.pdf",
        "personal_statement.pdf",
    ]
    requirements = (req.name, req.read_bytes())
    apps = [(n, (SAMPLES / n).read_bytes()) for n in app_names]
    return requirements, apps


def issue_detected(report_text: str, keywords: list[str]) -> bool:
    lower = report_text.lower()
    return any(k.lower() in lower for k in keywords)


def run_evaluation() -> dict:
    requirements, apps = load_demo_files()
    key = json.loads(ANSWER_KEY.read_text())

    provider = resolve_provider(
        "openrouter" if os.environ.get("OPENROUTER_API_KEY") else None
    )
    timeout = 600.0 if provider == "openrouter" else 1800.0
    client = create_llm_client(provider, timeout=timeout)
    if not client.is_available():
        return {
            "error": "No LLM available. Set OPENROUTER_API_KEY or start Ollama with gemma3:4b.",
            "ollama_available": False,
            "provider": provider,
        }

    start = time.perf_counter()
    try:
        report = run_analysis(requirements, apps, client=client)
    except LLMError as exc:
        return {"error": str(exc), "ollama_available": True}

    elapsed = time.perf_counter() - start

    combined = json.dumps(report.model_dump(), default=str)
    planted = key.get("planted_issues", [])
    detected = 0
    details = []
    for issue in planted:
        kws = issue.get("related_requirement_keywords") or []
        if issue.get("type") == "contradiction":
            kws = issue.get("fields", [])
        found = issue_detected(combined, kws) if kws else False
        if not found and issue.get("type") == "contradiction":
            found = len(report.contradictions) > 0
        if found:
            detected += 1
        details.append({"id": issue.get("id"), "detected": found})

    total_reqs = len(report.findings)
    verified = report.count_by_status(FindingStatus.VERIFIED)
    missing = report.count_by_status(FindingStatus.MISSING)
    review = report.count_by_status(FindingStatus.NEEDS_REVIEW)

    false_positive_proxy = max(0, verified - len(key.get("satisfied_examples", [])))
    planted_total = len(planted)
    planted_rate = (detected / planted_total) if planted_total else 0.0
    classified = verified + missing + review
    classification_rate = (classified / total_reqs) if total_reqs else 0.0

    return {
        "ollama_available": True,
        "provider": provider,
        "requirements_extracted": len(report.requirements),
        "findings_total": total_reqs,
        "verified": verified,
        "missing": missing,
        "needs_review": review,
        "not_applicable": report.count_by_status(FindingStatus.NOT_APPLICABLE),
        "contradictions": len(report.contradictions),
        "planted_issues_total": planted_total,
        "planted_issues_detected": detected,
        "planted_issues_detection_rate": round(planted_rate, 4),
        "planted_issue_details": details,
        "false_positive_proxy": false_positive_proxy,
        "requirements_classified_rate": round(classification_rate, 4),
        "average_analysis_time_seconds": round(report.analysis_duration_seconds, 2),
        "analysis_duration_seconds": report.analysis_duration_seconds,
        "wall_clock_seconds": round(elapsed, 2),
    }


def main() -> None:
    results = run_evaluation()
    out_dir = ROOT / "evaluation" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "latest.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()

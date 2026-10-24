"""Match analysis output to planted demo issues (ground-truth evaluation)."""

from __future__ import annotations

import re
from typing import Any, Optional

from core.schemas import AnalysisReport, Contradiction, FindingStatus, VerificationFinding


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def finding_text_blob(f: VerificationFinding) -> str:
    parts = [
        f.requirement_description,
        f.explanation,
        f.next_action,
        f.requirement_source.quotation,
    ]
    if f.evidence:
        parts.extend(
            [
                f.evidence.explanation or "",
                f.evidence.excerpt or "",
                f.evidence.document_filename or "",
            ]
        )
    return _norm(" ".join(parts))


def findings_for_requirement_keywords(
    report: AnalysisReport,
    keywords: list[str],
) -> list[VerificationFinding]:
    keys = [k.lower() for k in keywords]
    out: list[VerificationFinding] = []
    for f in report.findings:
        blob = _norm(f.requirement_description)
        if any(k in blob for k in keys):
            out.append(f)
    return out


def _status_ok(f: VerificationFinding, allowed: list[str]) -> bool:
    return f.status.value in allowed


def _text_has_any(blob: str, phrases: list[str]) -> bool:
    return any(p.lower() in blob for p in phrases)


def _text_has_all(blob: str, phrases: list[str]) -> bool:
    return all(p.lower() in blob for p in phrases)


def match_missing_document(
    report: AnalysisReport,
    spec: dict[str, Any],
) -> dict[str, Any]:
    keywords = spec.get("finding_requirement_contains", ["transcript"])
    allowed = spec.get("status_in", ["missing", "needs_review"])
    problem_phrases = spec.get("problem_phrases", [
        "not found",
        "missing",
        "not included",
        "not locate",
        "absent",
        "no evidence",
        "could not",
    ])
    candidates = findings_for_requirement_keywords(report, keywords)
    for f in candidates:
        blob = finding_text_blob(f)
        if not _status_ok(f, allowed):
            continue
        if f.status == FindingStatus.VERIFIED:
            continue
        if _text_has_any(blob, problem_phrases):
            return {
                "matched": True,
                "finding_id": f.requirement_id,
                "status": f.status.value,
                "reason": "Requirement on transcript with problem-oriented status and explanation.",
            }
    if candidates:
        f = candidates[0]
        return {
            "matched": False,
            "finding_id": f.requirement_id,
            "status": f.status.value,
            "reason": "Transcript-related finding found but did not meet problem text/status rules.",
        }
    return {"matched": False, "finding_id": None, "reason": "No transcript-related requirement finding."}


def match_contradiction_issue(
    report: AnalysisReport,
    spec: dict[str, Any],
) -> dict[str, Any]:
    field_keys = [k.lower() for k in spec.get("field_contains", ["graduation"])]
    value_patterns = spec.get("value_patterns", [r"2024", r"2025"])
    for c in report.contradictions:
        fn = c.field_name.lower()
        if not any(k in fn for k in field_keys):
            continue
        combined = _norm(c.explanation + " " + " ".join(v.raw_value for v in c.values))
        if all(re.search(p, combined, re.I) for p in value_patterns):
            return {
                "matched": True,
                "contradiction_id": c.id,
                "reason": "Graduation date contradiction with both years present.",
            }
    if report.contradictions:
        c = report.contradictions[0]
        return {
            "matched": False,
            "contradiction_id": c.id,
            "reason": "Contradictions present but graduation/year criteria not satisfied.",
        }
    return {"matched": False, "contradiction_id": None, "reason": "No contradictions reported."}


def match_finding_issue(
    report: AnalysisReport,
    spec: dict[str, Any],
) -> dict[str, Any]:
    keywords = spec.get("finding_requirement_contains", [])
    allowed = spec.get("status_in", ["missing", "needs_review"])
    problem_phrases = spec.get("problem_phrases", [])
    candidates = findings_for_requirement_keywords(report, keywords)
    for f in candidates:
        blob = finding_text_blob(f)
        if not _status_ok(f, allowed):
            continue
        if f.status == FindingStatus.VERIFIED and problem_phrases:
            continue
        if problem_phrases and not _text_has_any(blob, problem_phrases):
            continue
        return {
            "matched": True,
            "finding_id": f.requirement_id,
            "status": f.status.value,
            "reason": spec.get("success_reason", "Finding matched planted issue criteria."),
        }
    if candidates:
        f = candidates[0]
        return {
            "matched": False,
            "finding_id": f.requirement_id,
            "status": f.status.value,
            "reason": "Related finding exists but criteria for this planted issue were not met.",
        }
    return {"matched": False, "finding_id": None, "reason": "No related requirement finding."}


MATCHERS = {
    "missing_document": match_missing_document,
    "contradiction": match_contradiction_issue,
    "stale_document": match_finding_issue,
    "missing_signature": match_finding_issue,
    "eligibility": match_finding_issue,
}

DEFAULT_SPECS: dict[str, dict[str, Any]] = {
    "ISSUE-001": {
        "finding_requirement_contains": ["transcript"],
        "status_in": ["missing", "needs_review"],
        "problem_phrases": [
            "not found",
            "missing",
            "not included",
            "not locate",
            "absent",
            "no evidence",
            "could not",
            "not provided",
        ],
    },
    "ISSUE-002": {
        "field_contains": ["graduation"],
        "value_patterns": [r"2024", r"2025"],
    },
    "ISSUE-003": {
        "finding_requirement_contains": ["recommendation", "letter"],
        "status_in": ["missing", "needs_review"],
        "problem_phrases": [
            "november",
            "2024",
            "six month",
            "6 month",
            "outside",
            "stale",
            "window",
            "dated",
            "old",
            "expired",
        ],
    },
    "ISSUE-004": {
        "finding_requirement_contains": ["signature", "declaration", "signed"],
        "status_in": ["missing", "needs_review"],
        "problem_phrases": [
            "unsigned",
            "not signed",
            "signature",
            "blank",
            "missing sign",
            "without sign",
        ],
    },
    "ISSUE-005": {
        "finding_requirement_contains": ["gpa", "3.0", "grade", "cumulative"],
        "status_in": ["missing", "needs_review"],
        "problem_phrases": [
            "2.7",
            "below",
            "minimum",
            "under",
            "does not meet",
            "not meet",
            "less than",
        ],
    },
}


def evaluate_planted_issues(
    report: AnalysisReport,
    planted_issues: list[dict[str, Any]],
) -> dict[str, Any]:
    per_issue: list[dict[str, Any]] = []
    true_positives = 0

    for issue in planted_issues:
        issue_id = issue["id"]
        issue_type = issue.get("type", "")
        spec = {**DEFAULT_SPECS.get(issue_id, {}), **issue.get("match", {})}
        matcher = MATCHERS.get(issue_type)
        if not matcher:
            result = {"matched": False, "reason": f"No matcher for type {issue_type}"}
        elif issue_type == "contradiction":
            result = matcher(report, spec)
        else:
            result = matcher(report, spec)

        matched = bool(result.get("matched"))
        if matched:
            true_positives += 1
        per_issue.append(
            {
                "id": issue_id,
                "type": issue_type,
                "description": issue.get("description"),
                "matched": matched,
                **{k: v for k, v in result.items() if k != "matched"},
            }
        )

    total = len(planted_issues)
    false_negatives = total - true_positives

    # Findings that look like problems but don't map to any planted issue topic
    planted_topics = [
        "transcript",
        "graduation",
        "recommendation",
        "signature",
        "declaration",
        "gpa",
        "3.0",
    ]
    problem_findings: list[VerificationFinding] = []
    for f in report.findings:
        if f.status not in (FindingStatus.MISSING, FindingStatus.NEEDS_REVIEW):
            continue
        blob = _norm(f.requirement_description)
        if not any(t in blob for t in planted_topics):
            problem_findings.append(f)

    false_positive_findings = [
        {
            "requirement_id": f.requirement_id,
            "status": f.status.value,
            "description": f.requirement_description[:120],
        }
        for f in problem_findings
    ]

    recall = true_positives / total if total else 0.0
    # Precision: TP / (TP + extra problem findings on non-planted topics)
    fp_count = len(false_positive_findings)
    precision = true_positives / (true_positives + fp_count) if (true_positives + fp_count) else 0.0

    return {
        "planted_issue_recall": round(recall, 4),
        "planted_issue_precision": round(precision, 4),
        "true_positives": true_positives,
        "false_negatives": false_negatives,
        "false_positive_findings_count": fp_count,
        "false_positive_findings": false_positive_findings,
        "per_issue": per_issue,
    }

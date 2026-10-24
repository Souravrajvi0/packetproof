from core.schemas import (
    AnalysisReport,
    Contradiction,
    ContradictionSeverity,
    EvidenceMatch,
    ExtractedField,
    FindingStatus,
    ProvisionalMatchStatus,
    SourceReference,
    VerificationFinding,
)
from evaluation.planted_match import evaluate_planted_issues

PLANTED = [
    {"id": "ISSUE-001", "type": "missing_document", "description": "missing transcript"},
    {"id": "ISSUE-002", "type": "contradiction", "description": "grad dates"},
]


def test_planted_match_transcript_missing():
    report = AnalysisReport(
        requirements_pdf="r.pdf",
        application_documents=["a.pdf"],
        requirements=[],
        findings=[
            VerificationFinding(
                requirement_id="REQ-2",
                requirement_description="Official academic transcript required",
                status=FindingStatus.MISSING,
                explanation="Evidence not found for transcript in uploads.",
                requirement_source=SourceReference(filename="r.pdf", page_number=1, quotation="transcript"),
                next_action="Upload transcript",
            )
        ],
    )
    metrics = evaluate_planted_issues(report, PLANTED[:1])
    assert metrics["true_positives"] == 1
    assert metrics["planted_issue_recall"] == 1.0


def test_keyword_only_verified_does_not_count():
    report = AnalysisReport(
        requirements_pdf="r.pdf",
        application_documents=["a.pdf"],
        requirements=[],
        findings=[
            VerificationFinding(
                requirement_id="REQ-2",
                requirement_description="transcript required",
                status=FindingStatus.VERIFIED,
                explanation="Transcript keyword appears somewhere.",
                requirement_source=SourceReference(filename="r.pdf", page_number=1, quotation="x"),
                next_action="none",
                evidence=EvidenceMatch(
                    requirement_id="REQ-2",
                    explanation="ok",
                    provisional_status=ProvisionalMatchStatus.SUPPORTED,
                ),
            )
        ],
    )
    metrics = evaluate_planted_issues(report, PLANTED[:1])
    assert metrics["true_positives"] == 0


def test_contradiction_match():
    report = AnalysisReport(
        requirements_pdf="r.pdf",
        application_documents=["a.pdf"],
        requirements=[],
        contradictions=[
            Contradiction(
                id="CON-1",
                field_name="graduation_date",
                description="conflict",
                severity=ContradictionSeverity.HIGH,
                values=[
                    ExtractedField(
                        field_name="graduation_date",
                        normalized_value="2024",
                        raw_value="May 2024",
                        source=SourceReference(filename="a.pdf", page_number=1, quotation="May 2024"),
                    ),
                    ExtractedField(
                        field_name="graduation_date",
                        normalized_value="2025",
                        raw_value="June 2025",
                        source=SourceReference(filename="b.pdf", page_number=1, quotation="June 2025"),
                    ),
                ],
                explanation="May 2024 vs June 2025",
            )
        ],
    )
    metrics = evaluate_planted_issues(report, PLANTED[1:2])
    assert metrics["true_positives"] == 1

from core.contradictions import parse_date, values_conflict as vc
from core.pdf_processor import create_text_pdf, extract_pdf_from_bytes
from core.schemas import (
    EvidenceMatch,
    FindingStatus,
    ProvisionalMatchStatus,
    Requirement,
    RequirementCategory,
    SourceReference,
)
from core.verifier import build_findings, validate_evidence_match


def _req(req_id: str = "REQ-001") -> Requirement:
    return Requirement(
        id=req_id,
        description="Transcript required",
        category=RequirementCategory.DOCUMENT,
        expected_evidence="Official transcript",
        source=SourceReference(
            filename="req.pdf",
            page_number=1,
            quotation="official academic transcript",
        ),
    )


def test_missing_document_classification():
    data = create_text_pdf("req.pdf", ["An official academic transcript is required."])
    instructions = extract_pdf_from_bytes("req.pdf", data)
    match = EvidenceMatch(
        requirement_id="REQ-001",
        explanation="No transcript found.",
        provisional_status=ProvisionalMatchStatus.NOT_FOUND,
    )
    findings = build_findings([_req()], [match], instructions, [])
    assert findings[0].status == FindingStatus.MISSING


def test_invalid_page_reference():
    data = create_text_pdf("app.pdf", ["Some content"])
    doc = extract_pdf_from_bytes("app.pdf", data)
    match = EvidenceMatch(
        requirement_id="REQ-001",
        document_filename="app.pdf",
        page_number=99,
        excerpt="Some content",
        explanation="claimed",
        provisional_status=ProvisionalMatchStatus.SUPPORTED,
    )
    notes = validate_evidence_match(match, {"app.pdf": doc})
    assert any("out of range" in n for n in notes)


def test_invented_quote_rejected():
    data = create_text_pdf("app.pdf", ["Real text only"])
    doc = extract_pdf_from_bytes("app.pdf", data)
    match = EvidenceMatch(
        requirement_id="REQ-001",
        document_filename="app.pdf",
        page_number=1,
        excerpt="fabricated excerpt",
        explanation="claimed",
        provisional_status=ProvisionalMatchStatus.SUPPORTED,
    )
    notes = validate_evidence_match(match, {"app.pdf": doc})
    assert any("could not be verified" in n for n in notes)


def test_date_comparison():
    assert parse_date("2024-05-01") != parse_date("2025-06-01")
    assert vc("graduation_date", "May 2024", "June 2025")

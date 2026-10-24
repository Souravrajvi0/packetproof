from core.applicability import assess_applicability
from core.pdf_processor import create_text_pdf, extract_pdf_from_bytes
from core.schemas import Requirement, RequirementCategory, SourceReference
from core.verifier import build_findings
from core.schemas import EvidenceMatch, ProvisionalMatchStatus


def test_not_applicable_finding():
    req_pdf = create_text_pdf("req.pdf", ["International applicants need TOEFL."])
    instructions = extract_pdf_from_bytes("req.pdf", req_pdf)
    app_pdf = create_text_pdf("app.pdf", ["U.S. citizen, Northview High School"])
    app_doc = extract_pdf_from_bytes("app.pdf", app_pdf)

    conditional = Requirement(
        id="REQ-099",
        description="TOEFL required for international applicants",
        category=RequirementCategory.DOCUMENT,
        is_conditional=True,
        condition_description="Applies only to international applicants",
        expected_evidence="TOEFL score report",
        source=SourceReference(filename="req.pdf", page_number=1, quotation="International applicants"),
    )

    def mock_loader(prompt: str, system: str | None) -> object:
        return {
            "requirement_id": "REQ-099",
            "is_applicable": False,
            "explanation": "Applicant appears to be a U.S. domestic student.",
        }

    applicability = assess_applicability(
        [conditional], [app_doc], client=None, json_loader=mock_loader  # type: ignore[arg-type]
    )
    findings = build_findings(
        [conditional],
        [],
        instructions,
        [app_doc],
        applicability=applicability,
    )
    assert findings[0].status.value == "not_applicable"

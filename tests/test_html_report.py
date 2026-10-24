from core.schemas import AnalysisReport, FindingStatus, SourceReference, VerificationFinding
from reports.html_report import generate_html_report


def test_html_escapes_user_content():
    report = AnalysisReport(
        requirements_pdf="req.pdf",
        application_documents=["<script>.pdf"],
        requirements=[],
        findings=[
            VerificationFinding(
                requirement_id="REQ-001",
                requirement_description="<img onerror=alert(1)>",
                status=FindingStatus.MISSING,
                explanation="Test & demo",
                requirement_source=SourceReference(
                    filename="req.pdf", page_number=1, quotation='"<bad>"'
                ),
                next_action="Fix",
            )
        ],
    )
    html = generate_html_report(report)
    assert "<script>" not in html
    assert "&lt;img" in html

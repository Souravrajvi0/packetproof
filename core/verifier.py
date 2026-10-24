"""Evidence validation and finding classification."""

from __future__ import annotations

from core.pdf_processor import quote_exists_in_document
from core.schemas import (
    EvidenceMatch,
    FindingStatus,
    ProvisionalMatchStatus,
    Requirement,
    SourceReference,
    UploadedDocument,
    VerificationFinding,
)


def validate_source_reference(
    ref: SourceReference,
    documents: dict[str, UploadedDocument],
) -> list[str]:
    notes: list[str] = []
    doc = documents.get(ref.filename)
    if doc is None:
        notes.append(f"Source file '{ref.filename}' not found in uploaded set.")
        return notes
    if ref.page_number < 1 or ref.page_number > doc.page_count:
        notes.append(
            f"Page {ref.page_number} is out of range for {ref.filename} ({doc.page_count} pages)."
        )
        return notes
    if ref.quotation and not quote_exists_in_document(doc, ref.page_number, ref.quotation):
        notes.append("Requirement quotation could not be verified in the instruction PDF.")
    return notes


def validate_evidence_match(
    match: EvidenceMatch,
    documents: dict[str, UploadedDocument],
) -> list[str]:
    notes: list[str] = []
    if not match.document_filename:
        if match.provisional_status == ProvisionalMatchStatus.SUPPORTED:
            notes.append("Model claimed support but cited no document filename.")
        return notes

    doc = documents.get(match.document_filename)
    if doc is None:
        notes.append(f"Evidence file '{match.document_filename}' not found.")
        return notes

    if match.page_number is None:
        notes.append("Evidence page number missing.")
        return notes

    if match.page_number < 1 or match.page_number > doc.page_count:
        notes.append(
            f"Evidence page {match.page_number} out of range for {match.document_filename}."
        )
        return notes

    page = doc.pages[match.page_number - 1]
    if not page.is_readable:
        notes.append("Evidence page has little extractable text; manual review recommended.")

    if match.excerpt:
        if not quote_exists_in_document(doc, match.page_number, match.excerpt):
            notes.append("Supporting excerpt could not be verified in document text.")
    elif match.provisional_status == ProvisionalMatchStatus.SUPPORTED:
        notes.append("No verifiable excerpt provided for claimed support.")

    return notes


def classify_finding(
    requirement: Requirement,
    match: EvidenceMatch,
    validation_notes: list[str],
) -> tuple[FindingStatus, str, str]:
    has_invalid_ref = any(
        "not found" in n.lower() or "out of range" in n.lower() or "could not be verified" in n.lower()
        for n in validation_notes
    )

    if has_invalid_ref:
        return (
            FindingStatus.NEEDS_REVIEW,
            "Evidence references could not be fully verified. " + "; ".join(validation_notes),
            "Re-upload clearer documents or verify citations manually.",
        )

    status = match.provisional_status
    if status == ProvisionalMatchStatus.NOT_FOUND:
        return (
            FindingStatus.MISSING,
            match.explanation or "Required evidence was not located in uploaded documents.",
            "Obtain and upload the missing document or clarify with the program administrator.",
        )

    if status == ProvisionalMatchStatus.UNCERTAIN:
        return (
            FindingStatus.NEEDS_REVIEW,
            match.explanation,
            "Review the cited material and confirm it satisfies the requirement.",
        )

    if status == ProvisionalMatchStatus.PARTIAL:
        return (
            FindingStatus.NEEDS_REVIEW,
            match.explanation,
            "Provide additional or clearer evidence for this requirement.",
        )

    if status == ProvisionalMatchStatus.SUPPORTED:
        if validation_notes:
            return (
                FindingStatus.NEEDS_REVIEW,
                match.explanation + " Validation notes: " + "; ".join(validation_notes),
                "Confirm evidence manually due to validation warnings.",
            )
        return (
            FindingStatus.VERIFIED,
            match.explanation,
            "No action required unless you wish to double-check the cited evidence.",
        )

    return (
        FindingStatus.NEEDS_REVIEW,
        match.explanation,
        "Review this requirement manually.",
    )


def build_findings(
    requirements: list[Requirement],
    matches: list[EvidenceMatch],
    instructions_doc: UploadedDocument,
    application_docs: list[UploadedDocument],
) -> list[VerificationFinding]:
    doc_map: dict[str, UploadedDocument] = {
        instructions_doc.filename: instructions_doc,
    }
    for d in application_docs:
        doc_map[d.filename] = d

    match_by_id = {m.requirement_id: m for m in matches}
    findings: list[VerificationFinding] = []

    for req in requirements:
        match = match_by_id.get(
            req.id,
            EvidenceMatch(
                requirement_id=req.id,
                explanation="No evidence match was produced.",
                provisional_status=ProvisionalMatchStatus.UNCERTAIN,
            ),
        )

        notes = validate_source_reference(req.source, doc_map)
        notes.extend(validate_evidence_match(match, doc_map))

        status, explanation, next_action = classify_finding(req, match, notes)

        findings.append(
            VerificationFinding(
                requirement_id=req.id,
                requirement_description=req.description,
                status=status,
                explanation=explanation,
                requirement_source=req.source,
                evidence=match if match.document_filename or match.excerpt else None,
                next_action=next_action,
                validation_notes=notes,
            )
        )

    return findings


def document_coverage(
    application_docs: list[UploadedDocument],
    matches: list[EvidenceMatch],
) -> dict[str, int]:
    coverage: dict[str, int] = {d.filename: 0 for d in application_docs}
    for m in matches:
        if m.document_filename and m.document_filename in coverage:
            if m.provisional_status in (
                ProvisionalMatchStatus.SUPPORTED,
                ProvisionalMatchStatus.PARTIAL,
            ):
                coverage[m.document_filename] += 1
    return coverage

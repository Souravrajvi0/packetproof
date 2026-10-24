"""Pydantic data models for PacketProof."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class RequirementCategory(str, Enum):
    DOCUMENT = "document"
    ELIGIBILITY = "eligibility"
    FORMATTING = "formatting"
    DEADLINE = "deadline"
    OTHER = "other"


class FindingStatus(str, Enum):
    VERIFIED = "verified"
    MISSING = "missing"
    NEEDS_REVIEW = "needs_review"
    NOT_APPLICABLE = "not_applicable"


class ProvisionalMatchStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    NOT_FOUND = "not_found"
    UNCERTAIN = "uncertain"


class PageText(BaseModel):
    page_number: int = Field(ge=1)
    text: str
    is_readable: bool = True
    warning: Optional[str] = None


class UploadedDocument(BaseModel):
    filename: str
    page_count: int = Field(ge=0)
    pages: list[PageText] = Field(default_factory=list)
    extraction_warnings: list[str] = Field(default_factory=list)

    @property
    def full_text(self) -> str:
        parts: list[str] = []
        for p in self.pages:
            parts.append(f"[Page {p.page_number}]\n{p.text}")
        return "\n\n".join(parts)


class SourceReference(BaseModel):
    filename: str
    page_number: int = Field(ge=1)
    quotation: str

    def normalized_quotation(self) -> str:
        return " ".join(self.quotation.split())


class Requirement(BaseModel):
    id: str
    description: str
    category: RequirementCategory
    is_conditional: bool = False
    condition_description: Optional[str] = None
    expected_evidence: str
    source: SourceReference
    notes: Optional[str] = None


class EvidenceMatch(BaseModel):
    requirement_id: str
    document_filename: Optional[str] = None
    page_number: Optional[int] = None
    excerpt: Optional[str] = None
    explanation: str
    provisional_status: ProvisionalMatchStatus
    model_confidence_note: Optional[str] = None


class ExtractedField(BaseModel):
    field_name: str
    normalized_value: str
    raw_value: str
    source: SourceReference


class ContradictionSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Contradiction(BaseModel):
    id: str
    field_name: str
    description: str
    severity: ContradictionSeverity
    values: list[ExtractedField]
    explanation: str
    may_be_benign: bool = False


class VerificationFinding(BaseModel):
    requirement_id: str
    requirement_description: str
    status: FindingStatus
    explanation: str
    requirement_source: SourceReference
    evidence: Optional[EvidenceMatch] = None
    next_action: str
    validation_notes: list[str] = Field(default_factory=list)


class AnalysisReport(BaseModel):
    requirements_pdf: str
    application_documents: list[str]
    requirements: list[Requirement]
    provisional_matches: list[EvidenceMatch] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    findings: list[VerificationFinding] = Field(default_factory=list)
    document_coverage: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    analysis_duration_seconds: float = 0.0

    @property
    def applicable_count(self) -> int:
        return sum(1 for f in self.findings if f.status != FindingStatus.NOT_APPLICABLE)

    def count_by_status(self, status: FindingStatus) -> int:
        return sum(1 for f in self.findings if f.status == status)


class LLMError(Exception):
    """Raised when local LLM inference fails."""


class PDFExtractionError(Exception):
    """Raised when PDF cannot be processed safely."""


class ModelResponseValidationError(Exception):
    """Raised when model output cannot be validated."""

    def __init__(self, message: str, raw: Any = None):
        super().__init__(message)
        self.raw = raw

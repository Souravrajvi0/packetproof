import pytest

from core.ingest import document_from_text, ingest_bytes
from core.pdf_processor import create_text_pdf
from core.schemas import PDFExtractionError


def test_ingest_plain_text_file():
    doc = ingest_bytes("rules.txt", b"A transcript is required.\nGPA must be 3.0.")
    assert "transcript" in doc.full_text.lower()
    assert doc.pages[0].is_readable


def test_pasted_requirements():
    doc = document_from_text("pasted_requirements.txt", "Submit a government-issued photo ID.")
    assert doc.filename == "pasted_requirements.txt"
    assert "photo ID" in doc.full_text


def test_ingest_still_reads_pdf():
    data = create_text_pdf("r.pdf", ["Official transcript required"])
    doc = ingest_bytes("r.pdf", data)
    assert "transcript" in doc.full_text.lower()


def test_unsupported_type():
    with pytest.raises(PDFExtractionError):
        ingest_bytes("notes.docx", b"PK\x03\x04")


def test_image_without_vision_warns():
    # Minimal PNG header-ish bytes; no vision client
    doc = ingest_bytes("scan.png", b"\x89PNG\r\n" + b"\x00" * 40)
    assert not doc.pages[0].is_readable
    assert doc.extraction_warnings

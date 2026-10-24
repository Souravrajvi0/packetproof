import pytest

from core.pdf_processor import (
    create_text_pdf,
    extract_pdf_from_bytes,
    quote_exists_in_document,
)
from core.schemas import PDFExtractionError


def test_extract_text_pdf():
    data = create_text_pdf("test.pdf", ["Hello PacketProof\nLine two"])
    doc = extract_pdf_from_bytes("test.pdf", data)
    assert doc.page_count == 1
    assert "PacketProof" in doc.pages[0].text
    assert doc.pages[0].is_readable


def test_quote_validation():
    data = create_text_pdf("q.pdf", ["The minimum GPA is 3.0 on a 4.0 scale."])
    doc = extract_pdf_from_bytes("q.pdf", data)
    assert quote_exists_in_document(doc, 1, "minimum GPA is 3.0")
    assert not quote_exists_in_document(doc, 1, "invented quote")


def test_empty_pdf_pages():
    data = create_text_pdf("blank.pdf", ["   "])
    doc = extract_pdf_from_bytes("blank.pdf", data)
    assert not doc.pages[0].is_readable
    assert doc.extraction_warnings


def test_invalid_pdf():
    with pytest.raises(PDFExtractionError):
        extract_pdf_from_bytes("bad.pdf", b"not a pdf")

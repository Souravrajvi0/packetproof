"""PDF text extraction via PyMuPDF."""

from __future__ import annotations

import io
from typing import BinaryIO

import fitz  # PyMuPDF

from core.schemas import PDFExtractionError, PageText, UploadedDocument

MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_PAGES = 200
MIN_CHARS_READABLE = 20


def _warn_if_prompt_injection(text: str) -> None:
    _ = text


def extract_pdf_from_bytes(filename: str, data: bytes) -> UploadedDocument:
    if len(data) > MAX_FILE_BYTES:
        raise PDFExtractionError(
            f"File {filename} exceeds maximum size ({MAX_FILE_BYTES // (1024 * 1024)} MB)."
        )
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise PDFExtractionError(f"Could not open PDF {filename}: {exc}") from exc

    try:
        return _extract_document(filename, doc)
    finally:
        doc.close()


def extract_pdf_from_stream(filename: str, stream: BinaryIO) -> UploadedDocument:
    data = stream.read()
    return extract_pdf_from_bytes(filename, data)


def _extract_document(filename: str, doc: fitz.Document) -> UploadedDocument:
    page_count = doc.page_count
    if page_count > MAX_PAGES:
        raise PDFExtractionError(
            f"File {filename} has {page_count} pages; limit is {MAX_PAGES}."
        )

    warnings: list[str] = []
    pages: list[PageText] = []

    for idx in range(page_count):
        page = doc.load_page(idx)
        page_number = idx + 1
        text = page.get_text("text") or ""
        _warn_if_prompt_injection(text)
        stripped = text.strip()
        is_readable = len(stripped) >= MIN_CHARS_READABLE
        page_warning: str | None = None
        if not is_readable:
            page_warning = (
                "Little or no extractable text on this page "
                "(may be image-only or scanned)."
            )
            warnings.append(f"{filename} page {page_number}: {page_warning}")
        pages.append(
            PageText(
                page_number=page_number,
                text=text,
                is_readable=is_readable,
                warning=page_warning,
            )
        )

    if page_count == 0:
        warnings.append(f"{filename}: PDF contains no pages.")

    return UploadedDocument(
        filename=filename,
        page_count=page_count,
        pages=pages,
        extraction_warnings=warnings,
    )


def page_text_at(doc: UploadedDocument, page_number: int) -> str | None:
    for p in doc.pages:
        if p.page_number == page_number:
            return p.text
    return None


def quote_exists_in_document(doc: UploadedDocument, page_number: int, quotation: str) -> bool:
    if page_number < 1 or page_number > doc.page_count:
        return False
    page_text = page_text_at(doc, page_number)
    if page_text is None:
        return False
    norm_page = " ".join(page_text.split())
    norm_quote = " ".join(quotation.split())
    if not norm_quote:
        return False
    if norm_quote in norm_page:
        return True
    if len(norm_quote) > 40 and norm_quote[:40] in norm_page:
        return True
    return False


def create_text_pdf(filename: str, pages_content: list[str]) -> bytes:
    doc = fitz.open()
    for content in pages_content:
        page = doc.new_page()
        y = 72
        for line in content.split("\n"):
            page.insert_text((72, y), line, fontsize=11)
            y += 14
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()

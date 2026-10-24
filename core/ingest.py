"""Ingest PDFs, plain text, pasted notes, and photos into UploadedDocument."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.pdf_processor import MAX_FILE_BYTES, MIN_CHARS_READABLE, extract_pdf_from_bytes
from core.schemas import PDFExtractionError, PageText, UploadedDocument

TEXT_SUFFIXES = {".txt", ".md", ".text", ".rst"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
PDF_SUFFIXES = {".pdf"}

VISION_PROMPT = (
    "Extract ALL visible text from this image of application instructions or a "
    "supporting document. Preserve headings and lists. Do not invent text that is "
    "not visible. If the image is unreadable, say so. Output plain text only."
)


def document_from_text(filename: str, text: str, warning: Optional[str] = None) -> UploadedDocument:
    stripped = (text or "").strip()
    readable = len(stripped) >= MIN_CHARS_READABLE
    warnings: list[str] = []
    if warning:
        warnings.append(warning)
    if not readable:
        warnings.append(f"{filename}: little or no extractable text.")
    return UploadedDocument(
        filename=filename,
        page_count=1,
        pages=[
            PageText(
                page_number=1,
                text=text or "",
                is_readable=readable,
                warning=None if readable else "Little or no extractable text.",
            )
        ],
        extraction_warnings=warnings,
    )


def _suffix(filename: str) -> str:
    return Path(filename).suffix.lower()


def ingest_bytes(
    filename: str,
    data: bytes,
    vision_client: Optional[object] = None,
) -> UploadedDocument:
    if len(data) > MAX_FILE_BYTES:
        raise PDFExtractionError(
            f"File {filename} exceeds maximum size ({MAX_FILE_BYTES // (1024 * 1024)} MB)."
        )
    suffix = _suffix(filename)
    if suffix in PDF_SUFFIXES:
        return extract_pdf_from_bytes(filename, data)
    if suffix in TEXT_SUFFIXES or suffix == "":
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-8", errors="replace")
        return document_from_text(filename, text)
    if suffix in IMAGE_SUFFIXES:
        return _ingest_image(filename, data, vision_client)
    raise PDFExtractionError(
        f"Unsupported file type for {filename}. Use PDF, TXT, MD, PNG, JPG, or WEBP."
    )


def _ingest_image(
    filename: str,
    data: bytes,
    vision_client: Optional[object],
) -> UploadedDocument:
    extractor = getattr(vision_client, "generate_from_image", None) if vision_client else None
    if extractor is None:
        return document_from_text(
            filename,
            "",
            warning=(
                f"{filename} is an image. Select Gemma (Ollama or OpenRouter) and re-upload "
                "so the photo can be transcribed, or paste the text instead."
            ),
        )
    try:
        text = extractor(VISION_PROMPT, data, filename)
    except Exception as exc:
        return document_from_text(
            filename,
            "",
            warning=f"Could not read text from image {filename}: {exc}",
        )
    return document_from_text(
        filename,
        text,
        warning=f"Text transcribed from image {filename} by Gemma (may contain OCR errors).",
    )

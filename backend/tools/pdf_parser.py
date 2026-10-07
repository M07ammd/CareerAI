"""
CareerPilot AI - PDF Parser Tool

Extracts clean text from uploaded PDF files using PyMuPDF (fitz).
Falls back to pdfplumber if fitz is not available.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


def _clean_text(raw: str) -> str:
    """Normalise whitespace and remove junk characters."""
    text = re.sub(r"\n{3,}", "\n\n", raw)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def extract_text_from_pdf(
    file_content: bytes,
    filename: str = "resume.pdf",
    max_pages: int = 50,
    max_chars: int = 30_000,
) -> str:
    """
    Extract plain text from a PDF byte string.

    Args:
        file_content: Raw bytes of the PDF file.
        filename:     Original file name (used only for logging, NOT logged as PII).
        max_pages:    Maximum number of pages to read (protects against huge PDFs).
        max_chars:    Maximum characters to return (truncates silently).

    Returns:
        Extracted text as a single string (up to max_chars).

    Raises:
        ValueError: If the file is empty, not a PDF, or no text could be extracted.
    """
    if not file_content:
        raise ValueError("PDF file content is empty.")

    if file_content[:4] != b"%PDF":
        raise ValueError("File does not appear to be a valid PDF (bad magic bytes).")

    text = _try_pymupdf(file_content, max_pages) or _try_pdfplumber(file_content, max_pages)

    if not text or len(text.strip()) < 50:
        raise ValueError(
            "Could not extract meaningful text from the PDF. "
            "The file may be scanned/image-based or password-protected."
        )

    cleaned = _clean_text(text)
    logger.info("Extracted %d characters from PDF (%d byte input)", len(cleaned), len(file_content))

    # Truncate to max_chars to stay within LLM context limits
    if len(cleaned) > max_chars:
        logger.warning("Resume text truncated from %d to %d chars", len(cleaned), max_chars)
        cleaned = cleaned[:max_chars]

    return cleaned


def _try_pymupdf(content: bytes, max_pages: int) -> str:
    """Attempt extraction with PyMuPDF (fitz)."""
    try:
        import fitz  # type: ignore  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        pages = [doc[i].get_text("text") for i in range(min(len(doc), max_pages))]
        doc.close()
        return "\n".join(pages)
    except ImportError:
        logger.debug("PyMuPDF not available; trying pdfplumber")
        return ""
    except Exception as exc:
        logger.warning("PyMuPDF extraction failed: %s", exc)
        return ""


def _try_pdfplumber(content: bytes, max_pages: int) -> str:
    """Attempt extraction with pdfplumber."""
    try:
        import io
        import pdfplumber  # type: ignore

        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages[:max_pages]]
        return "\n".join(pages)
    except ImportError:
        logger.debug("pdfplumber not available")
        return ""
    except Exception as exc:
        logger.warning("pdfplumber extraction failed: %s", exc)
        return ""


def extract_text_from_file(file_path: Union[str, Path]) -> str:
    """Convenience wrapper to extract text from a PDF path."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return extract_text_from_pdf(path.read_bytes(), filename=path.name)

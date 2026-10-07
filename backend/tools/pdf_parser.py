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
    # collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", raw)
    # collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def extract_text_from_pdf(file_content: bytes, filename: str = "resume.pdf") -> str:
    """
    Extract plain text from a PDF byte string.

    Args:
        file_content: Raw bytes of the PDF file.
        filename:     Original file name (used only for logging).

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the file is empty, not a PDF, or no text could be extracted.
    """
    if not file_content:
        raise ValueError("PDF file content is empty.")

    # Basic magic-byte check – PDF files start with %PDF
    if not file_content[:4] == b"%PDF":
        raise ValueError(f"File '{filename}' does not appear to be a valid PDF.")

    text = _try_pymupdf(file_content) or _try_pdfplumber(file_content)

    if not text or len(text.strip()) < 50:
        raise ValueError(
            "Could not extract meaningful text from the PDF. "
            "The file may be scanned/image-based or password-protected."
        )

    logger.info("Extracted %d characters from '%s'", len(text), filename)
    return _clean_text(text)


def _try_pymupdf(content: bytes) -> str:
    """Attempt extraction with PyMuPDF (fitz)."""
    try:
        import fitz  # type: ignore  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        pages = [page.get_text("text") for page in doc]  # type: ignore[attr-defined]
        doc.close()
        return "\n".join(pages)
    except ImportError:
        logger.debug("PyMuPDF not available; trying pdfplumber")
        return ""
    except Exception as exc:
        logger.warning("PyMuPDF extraction failed: %s", exc)
        return ""


def _try_pdfplumber(content: bytes) -> str:
    """Attempt extraction with pdfplumber."""
    try:
        import io

        import pdfplumber  # type: ignore

        with pdfplumber.open(io.BytesIO(content)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages)
    except ImportError:
        logger.debug("pdfplumber not available")
        return ""
    except Exception as exc:
        logger.warning("pdfplumber extraction failed: %s", exc)
        return ""


def extract_text_from_file(file_path: Union[str, Path]) -> str:
    """
    Convenience wrapper to extract text from a PDF path.

    Args:
        file_path: Absolute or relative path to a PDF file.

    Returns:
        Extracted text string.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    content = path.read_bytes()
    return extract_text_from_pdf(content, filename=path.name)

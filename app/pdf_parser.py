# File: `app/pdf_parser.py`
import base64
import fitz  # PyMuPDF
from typing import Union


def _to_bytes(pdf_input: Union[bytes, str, list]) -> bytes:
    """Normalize input to raw PDF bytes (accepts bytes, base64/str, or list of lines)."""
    if isinstance(pdf_input, bytes):
        return pdf_input
    if isinstance(pdf_input, list):
        parts = []
        for item in pdf_input:
            parts.append(item if isinstance(item, bytes) else str(item).encode("latin-1"))
        return b"".join(parts)
    if isinstance(pdf_input, str):
        s = pdf_input.strip()
        # Try base64 decode first
        try:
            decoded = base64.b64decode(s, validate=True)
            if decoded.startswith(b"%PDF-"):
                return decoded
        except Exception:
            pass
        # fallback: treat as raw PDF text encoded with latin-1
        return s.encode("latin-1")
    raise TypeError("Unsupported pdf_input type")


def _repair_eof(pdf_bytes: bytes) -> bytes:
    """Trim anything after the last '%%EOF' or append '%%EOF' if missing."""
    lines = pdf_bytes.splitlines(keepends=True)
    for i in range(len(lines) - 1, -1, -1):
        if b"%%EOF" in lines[i]:
            return b"".join(lines[: i + 1])
    # no EOF found -> if looks like PDF, append EOF marker
    if pdf_bytes.startswith(b"%PDF-"):
        return pdf_bytes + b"\n%%EOF\n"
    return pdf_bytes


def extract_text_from_pdf(pdf_input: Union[bytes, str, list]) -> str:
    """
    Extract text content from a PDF using PyMuPDF with repair attempts.

    Args:
        pdf_input: raw bytes, base64/text string, or list of lines (bytes/str)

    Returns:
        Extracted text (empty string on failure)
    """
    pdf_bytes = _to_bytes(pdf_input)

    # Try normal open first, then attempt repair if it fails.
    for attempt in ("original", "repaired"):
        try:
            if attempt == "original":
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            else:
                repaired = _repair_eof(pdf_bytes)
                doc = fitz.open(stream=repaired, filetype="pdf")

            text = "".join(page.get_text() for page in doc)
            doc.close()
            return text.strip()
        except Exception as e:
            # If original failed, loop will try repaired; else fallthrough to return ""
            print(f"PDF parse attempt '{attempt}' failed: {e}")

    return ""


def validate_pdf(pdf_input: Union[bytes, str, list]) -> tuple[bool, str]:
    """
    Validate a PDF by trying to open it (with a repair attempt).

    Args:
        pdf_input: raw bytes, base64/text string, or list of lines (bytes/str)

    Returns:
        True if PyMuPDF can open and there is at least one page
    """
    pdf_bytes = _to_bytes(pdf_input)

    for attempt in ("original", "repaired"):
        try:
            if attempt == "original":
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            else:
                repaired = _repair_eof(pdf_bytes)
                doc = fitz.open(stream=repaired, filetype="pdf")

            is_valid = doc.page_count > 0
            doc.close()
            return (True, "Valid PDF") if is_valid else (False, "PDF has no pages")

        except Exception as e:
            error_msg = str(e)
            print(f"Invalid PDF file on attempt '{attempt}': {e}")

    return False, error_msg if 'error_msg' in locals() else "Unknown error"

"""POST /extract-pdf — pull selectable text out of an uploaded resume PDF.

Server-side extraction with pypdf (pure Python, no system deps). The returned
text is meant to populate the resume field the user then reviews/edits before
analyzing — we never analyze straight from the file blindly.
"""

import io
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/extract-pdf")
async def extract_pdf(file: UploadFile = File(...)) -> dict:
    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a .pdf file.")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB).")

    try:
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception as e:
        logger.exception("pdf parse failed")
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {e}") from e

    if not text:
        raise HTTPException(
            status_code=422,
            detail="No selectable text found — this looks like a scanned/image PDF. Paste the text instead.",
        )

    return {"text": text, "pages": len(reader.pages)}

"""POST /generate-latex — produce a tailored, compilable LaTeX resume.

Uses the stronger writer model and a plain-text completion (LaTeX doesn't survive
JSON mode well). The prompt forbids inventing experience — same truthfulness
guardrail as the bullet rewriter.
"""

import logging
import re

from fastapi import APIRouter, HTTPException

from app import latex_template, prompts
from app.core import llm
from app.core.config import settings
from app.models import LatexRequest

logger = logging.getLogger(__name__)
router = APIRouter()


def _strip_fences(text: str) -> str:
    """Remove ```latex / ``` fences if the model added them despite instructions."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.endswith("```"):
            t = t[: t.rfind("```")]
    return t.strip()


def _inner_body(text: str) -> str:
    """Extract just the body if the model wrapped it in preamble/document tags anyway."""
    body = _strip_fences(text)
    if "\\begin{document}" in body:
        body = body.split("\\begin{document}", 1)[1]
    if "\\end{document}" in body:
        body = body.split("\\end{document}", 1)[0]
    return body.strip()


_UNICODE_FIXES = {
    "–": "--", "—": "---",       # en / em dash
    "‘": "`", "’": "'",           # curly single quotes
    "“": "``", "”": "''",         # curly double quotes
    "•": r"\textbullet{} ", "…": r"\ldots{} ",
    " ": " ", "­": "",            # nbsp, soft hyphen
}


def _sanitize(body: str) -> str:
    """Make model-generated LaTeX actually compile. Three classes of fix:

    1. Normalize Unicode punctuation from the PDF text (en-dashes etc. that some
       fonts lack and would silently drop).
    2. Escape bare specials. A raw % is the dangerous one: it comments out the rest
       of the line — including the closing } of \\resumeItem{...} — causing a
       "runaway argument" and no PDF. Only escape chars NOT already backslash-escaped
       ($ is skipped since $|$ separators use it).
    3. Drop EMPTY itemize blocks. An itemize with no \\item throws "missing \\item";
       the model emits these under entries that have no bullets (e.g. Education)."""
    for uni, tex in _UNICODE_FIXES.items():
        body = body.replace(uni, tex)
    for ch in ("%", "&", "#"):
        body = re.sub(r"(?<!\\)" + re.escape(ch), "\\" + ch, body)
    body = re.sub(r"\\resumeItemListStart\s*\\resumeItemListEnd", "", body)
    body = re.sub(r"\\resumeSubHeadingListStart\s*\\resumeSubHeadingListEnd", "", body)
    return body


@router.post("/generate-latex")
def generate_latex(req: LatexRequest) -> dict:
    try:
        raw = llm.complete_text(
            prompts.latex_prompt(
                req.resume_text,
                req.jd_text,
                req.jd_keywords,
                req.tailored,
                latex_template.MACRO_GUIDE,
            ),
            model=settings.WRITER_MODEL,
            temperature=0.3,
        )
    except Exception as e:
        logger.exception("latex generation failed")
        raise HTTPException(status_code=502, detail=f"LaTeX generation failed: {e}") from e

    body = _inner_body(raw)
    if "\\section" not in body:
        raise HTTPException(status_code=502, detail="Model did not return valid resume content. Try again.")

    body = _sanitize(body)
    latex = latex_template.PREAMBLE + body + latex_template.CLOSING
    return {"latex": latex}

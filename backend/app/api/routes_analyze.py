"""POST /analyze — runs the PitchPerfect agent graph.

The JD analysis, resume match, and bullet rewrites are produced by a LangGraph
graph (analyzer -> matcher -> writer). The HTTP contract is unchanged from the
earlier inline version, so the frontend is untouched.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.agents.graph import resume_graph
from app.models import AnalyzeRequest, AnalyzeResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    try:
        final = resume_graph.invoke(
            {"jd_text": req.jd_text, "resume_text": req.resume_text}
        )
    except Exception as e:  # provider/network/validation errors surface as 502
        logger.exception("analyze graph failed")
        raise HTTPException(status_code=502, detail=f"Analysis failed: {e}") from e

    return AnalyzeResponse(
        analysis=final["analysis"],
        match=final["match"],
        tailored=final["tailored"],
    )

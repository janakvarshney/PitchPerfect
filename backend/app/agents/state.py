"""Shared state passed between agents in the graph.

Each node reads the inputs it needs and writes its own output key, so nodes never
clobber each other. total=False lets nodes return partial updates."""

from typing import TypedDict

from app.models import JDAnalysis, MatchResult, TailoredBullets


class ResumeState(TypedDict, total=False):
    # inputs
    jd_text: str
    resume_text: str
    # agent outputs
    analysis: JDAnalysis
    match: MatchResult
    tailored: TailoredBullets

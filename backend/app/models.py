"""Pydantic schemas — shared contract between the LLM, the API, and the frontend."""

from pydantic import BaseModel, Field


# ---- LLM structured outputs ----

class JDAnalysis(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)
    seniority: str = ""
    keywords: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


class MatchResult(BaseModel):
    matched: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    match_score: int = Field(0, ge=0, le=100)
    rationale: str = ""


class TailoredBullet(BaseModel):
    original: str
    rewritten: str


class TailoredBullets(BaseModel):
    bullets: list[TailoredBullet] = Field(default_factory=list)


# ---- API request / response ----

class AnalyzeRequest(BaseModel):
    jd_text: str = Field(..., min_length=1)
    resume_text: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    analysis: JDAnalysis
    match: MatchResult
    tailored: TailoredBullets


class LatexRequest(BaseModel):
    resume_text: str = Field(..., min_length=1)
    jd_text: str = ""
    jd_keywords: list[str] = Field(default_factory=list)
    tailored: list[TailoredBullet] = Field(default_factory=list)

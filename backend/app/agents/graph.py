"""The PitchPerfect agent graph (LangGraph).

Three specialized agents share one state object:

    START ─▶ analyzer ─▶ matcher ─▶ writer ─▶ END

- analyzer: extracts structured requirements from the job description
- matcher:  scores the resume against the job and finds gaps
- writer:   rewrites resume bullets tailored to the job (uses the stronger model)

The graph is compiled once at import and invoked by the /analyze route. The HTTP
contract is unchanged — this is a structural refactor of the previous inline calls,
with room to grow (e.g. a human-approval interrupt before the writer, or feeding the
analysis into the matcher/writer for richer context)."""

from langgraph.graph import END, START, StateGraph

from app import prompts
from app.agents.state import ResumeState
from app.core import llm
from app.core.config import settings
from app.models import JDAnalysis, MatchResult, TailoredBullets


def analyzer(state: ResumeState) -> dict:
    analysis = llm.complete_json(
        prompts.analyze_prompt(state["jd_text"]),
        JDAnalysis,
        model=settings.DEFAULT_MODEL,
    )
    return {"analysis": analysis}


def matcher(state: ResumeState) -> dict:
    match = llm.complete_json(
        prompts.match_prompt(state["jd_text"], state["resume_text"]),
        MatchResult,
        model=settings.DEFAULT_MODEL,
    )
    return {"match": match}


def writer(state: ResumeState) -> dict:
    tailored = llm.complete_json(
        prompts.rewrite_prompt(state["jd_text"], state["resume_text"]),
        TailoredBullets,
        model=settings.WRITER_MODEL,
    )
    return {"tailored": tailored}


def _build():
    g = StateGraph(ResumeState)
    g.add_node("analyzer", analyzer)
    g.add_node("matcher", matcher)
    g.add_node("writer", writer)
    g.add_edge(START, "analyzer")
    g.add_edge("analyzer", "matcher")
    g.add_edge("matcher", "writer")
    g.add_edge("writer", END)
    return g.compile()


# Compiled once, reused per request.
resume_graph = _build()

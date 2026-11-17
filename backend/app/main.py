from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_analyze, routes_latex, routes_resume
from app.core.config import settings

app = FastAPI(title="PitchPerfect API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # Allow any Vercel deployment (production + preview URLs) without hardcoding the domain.
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_analyze.router)
app.include_router(routes_resume.router)
app.include_router(routes_latex.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "provider": settings.LLM_PROVIDER, "model": settings.DEFAULT_MODEL}

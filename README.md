# PitchPerfect

An AI copilot that turns any job description into a tailored resume, a match score,
and (later) a tracked application — in minutes instead of an hour.

Built with a **portable, provider-agnostic** stack so it runs on personal accounts
with **no paid API and no company infrastructure**.

## Stack
- **Backend:** FastAPI (Python)
- **Frontend:** Next.js + TypeScript + Tailwind
- **LLM:** Free tier via **Groq** (OpenAI-compatible), swappable to local **Ollama** with one env var
- **Agents:** LangGraph *(added in a later increment)*
- **DB/Auth:** Supabase *(added in a later increment)*

## Current status: MVP loop (single LLM call)
Paste a job description + your resume → get extracted requirements, a match score,
and rewritten resume bullets.

## Quick start

### 1. Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev                 # http://localhost:3000
```

### Get a free Groq key
Sign up at https://console.groq.com with a **personal** email, create an API key,
and paste it into `backend/.env` as `GROQ_API_KEY`.

### Use local Ollama instead (fully offline, $0)
```bash
brew install ollama && ollama pull llama3.1
# in backend/.env:  LLM_PROVIDER=ollama
```

## Architecture
```
Next.js UI  ──HTTP──▶  FastAPI  ──▶  core/llm.py (Groq | Ollama)
                          │
                          └─ analyze → match → rewrite  (single-call MVP)
```

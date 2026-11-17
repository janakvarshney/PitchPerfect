# Deploying PitchPerfect

Backend → **Railway**, Frontend → **Vercel**. Both free tiers, personal accounts.
Everything below uses your own accounts — no company infrastructure.

---

## 0. Before you start
- **Regenerate your Groq API key** at https://console.groq.com (the old one was shared in chat). You'll paste the new one into Railway, never into git.
- Create a **personal GitHub repo** (e.g. `applypilot`). Do NOT use a company org.

## 1. Push the code (run these yourself)
```bash
cd /Users/auniyal/Documents/Codebase/applypilot
git remote add origin https://github.com/<your-username>/applypilot.git
git branch -M main
git push -u origin main
```
`.env`, `node_modules`, and `.venv` are gitignored, so no secrets or bulk files ship.

## 2. Backend → Railway
1. https://railway.app → **New Project → Deploy from GitHub repo** → pick your repo.
2. In the service **Settings**:
   - **Root Directory:** `backend`
   - Start command is auto-read from `backend/Procfile` (uvicorn on `$PORT`).
3. In **Variables**, add:
   | Key | Value |
   |-----|-------|
   | `LLM_PROVIDER` | `groq` |
   | `GROQ_API_KEY` | *your NEW Groq key* |
   | `CORS_ORIGINS` | *(leave blank for now; set in step 4)* |
4. Deploy. Copy the public URL Railway gives you, e.g. `https://applypilot-production.up.railway.app`.
5. Test it: open `<railway-url>/health` → should return `{"status":"ok",...}`.

## 2b. Backend → Render (free tier alternative — recommended for $0)
Uses the `render.yaml` blueprint at the repo root, so it's basically one click.
1. https://render.com → **New + → Blueprint** → connect GitHub → pick the **PitchPerfect** repo.
2. Render reads `render.yaml` and creates the `pitchperfect-api` web service (root `backend`, Python).
3. When prompted, set **`GROQ_API_KEY`** = *your NEW Groq key* (it's marked `sync:false`, so it stays out of git).
4. Deploy. Copy the URL, e.g. `https://pitchperfect-api.onrender.com`, and open `<url>/health`.
5. Note: the free tier **sleeps after ~15 min idle**, so the first request after a nap takes ~30–60s to wake.

## 3. Frontend → Vercel
1. https://vercel.com → **Add New → Project** → import the same GitHub repo.
2. **Root Directory:** `frontend` (Vercel auto-detects Next.js).
3. **Environment Variables** → add:
   | Key | Value |
   |-----|-------|
   | `NEXT_PUBLIC_API_URL` | *your Railway backend URL from step 2.4* |
4. Deploy. Copy the Vercel URL, e.g. `https://applypilot.vercel.app`.

## 4. Wire CORS (optional but tidy)
The backend already allows any `*.vercel.app` origin via regex, so it works out of the box.
If you use a custom domain later, add it to Railway's `CORS_ORIGINS` (comma-separated).

## 5. Done
Open your Vercel URL, upload a resume, paste a JD, Analyze. Put the link on your
resume/LinkedIn/GitHub.

---

### Notes
- The backend generates `.tex` only; no LaTeX toolchain is needed on the server (you
  compile on Overleaf).
- Free-tier Groq has a daily token cap; the app auto-falls-back from the 70B to the 8B
  model on a 429 (see `FALLBACK_MODEL`).
- Railway free tier may sleep on inactivity; the first request after idle can be slow.

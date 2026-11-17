// Typed client for the PitchPerfect backend. Mirrors backend/app/models.py.

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface JDAnalysis {
  required_skills: string[];
  nice_to_have: string[];
  seniority: string;
  keywords: string[];
  responsibilities: string[];
}

export interface MatchResult {
  matched: string[];
  gaps: string[];
  match_score: number;
  rationale: string;
}

export interface TailoredBullet {
  original: string;
  rewritten: string;
}

export interface AnalyzeResponse {
  analysis: JDAnalysis;
  match: MatchResult;
  tailored: { bullets: TailoredBullet[] };
}

export async function generateLatex(
  resume_text: string,
  jd_text: string,
  jd_keywords: string[],
  tailored: TailoredBullet[]
): Promise<{ latex: string }> {
  const res = await fetch(`${API_URL}/generate-latex`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text, jd_text, jd_keywords, tailored }),
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }

  return res.json();
}

export async function extractPdf(
  file: File
): Promise<{ text: string; pages: number }> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_URL}/extract-pdf`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    let detail = `Upload failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }

  return res.json();
}

export async function analyze(
  jd_text: string,
  resume_text: string
): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jd_text, resume_text }),
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }

  return res.json();
}

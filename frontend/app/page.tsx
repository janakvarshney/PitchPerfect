"use client";

import { useRef, useState } from "react";
import { analyze, extractPdf, generateLatex, AnalyzeResponse } from "@/lib/api";

export default function Home() {
  const [jd, setJd] = useState("");
  const [resume, setResume] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadNote, setUploadNote] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setUploadNote(null);
    setUploading(true);
    try {
      const { text, pages } = await extractPdf(file);
      setResume(text);
      setUploadNote(`Loaded "${file.name}" (${pages} page${pages === 1 ? "" : "s"}). Review before analyzing.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = ""; // allow re-uploading same file
    }
  }

  async function onAnalyze() {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await analyze(jd, resume);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  const canSubmit = jd.trim().length > 0 && resume.trim().length > 0 && !loading;

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">PitchPerfect</h1>
        <p className="mt-1 text-slate-600">
          Paste a job description and your resume. Get the requirements, a match
          score, and tailored bullet points.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        <Field
          label="Job description"
          value={jd}
          onChange={setJd}
          placeholder="Paste the full job posting here…"
        />
        <Field
          label="Your resume"
          value={resume}
          onChange={setResume}
          placeholder="Paste your resume, or upload a PDF above…"
          action={
            <>
              <input
                ref={fileRef}
                type="file"
                accept="application/pdf,.pdf"
                onChange={onUpload}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                disabled={uploading}
                className="rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 transition hover:bg-slate-100 disabled:opacity-50"
              >
                {uploading ? "Reading…" : "Upload PDF"}
              </button>
            </>
          }
        />
      </div>

      {uploadNote && (
        <p className="mt-2 text-sm text-green-700">{uploadNote}</p>
      )}

      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={onAnalyze}
          disabled={!canSubmit}
          className="rounded-md bg-slate-900 px-4 py-2 font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
        {loading && <span className="text-sm text-slate-500">Calling the model — this can take a few seconds.</span>}
      </div>

      {error && (
        <div className="mt-6 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {result && <Results data={result} />}
      {result && <LatexExport resume={resume} jd={jd} result={result} />}
    </main>
  );
}

function LatexExport({
  resume,
  jd,
  result,
}: {
  resume: string;
  jd: string;
  result: AnalyzeResponse;
}) {
  const [latex, setLatex] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function generate() {
    setErr(null);
    setLatex(null);
    setLoading(true);
    try {
      const { latex } = await generateLatex(
        resume,
        jd,
        result.analysis.keywords,
        result.tailored.bullets
      );
      setLatex(latex);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Failed to generate LaTeX");
    } finally {
      setLoading(false);
    }
  }

  function download() {
    if (!latex) return;
    const blob = new Blob([latex], { type: "application/x-tex" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "resume.tex";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function copy() {
    if (!latex) return;
    await navigator.clipboard.writeText(latex);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <section className="mt-8">
      <div className="rounded-lg border border-slate-200 bg-white p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              LaTeX résumé
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              A tailored, compilable <code>.tex</code> — paste it into{" "}
              <a
                href="https://www.overleaf.com"
                target="_blank"
                rel="noreferrer"
                className="underline hover:text-slate-700"
              >
                Overleaf
              </a>{" "}
              to get a PDF.
            </p>
          </div>
          <button
            onClick={generate}
            disabled={loading}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:opacity-40"
          >
            {loading ? "Generating…" : latex ? "Regenerate" : "Generate LaTeX résumé"}
          </button>
        </div>

        {err && (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {err}
          </div>
        )}

        {latex && (
          <div className="mt-4">
            <div className="mb-2 flex gap-2">
              <button
                onClick={copy}
                className="rounded-md border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
              >
                {copied ? "Copied ✓" : "Copy"}
              </button>
              <button
                onClick={download}
                className="rounded-md border border-slate-300 bg-white px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
              >
                Download .tex
              </button>
            </div>
            <pre className="max-h-96 overflow-auto rounded-md border border-slate-200 bg-slate-900 p-4 text-xs leading-relaxed text-slate-100">
              {latex}
            </pre>
          </div>
        )}
      </div>
    </section>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  action,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  action?: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">{label}</span>
        {action}
      </span>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={12}
        className="rounded-md border border-slate-300 bg-white p-3 text-sm outline-none focus:border-slate-500"
      />
    </label>
  );
}

function Results({ data }: { data: AnalyzeResponse }) {
  const { analysis, match, tailored } = data;
  return (
    <section className="mt-10 space-y-8">
      <ScoreCard score={match.match_score} rationale={match.rationale} />

      <div className="grid gap-6 md:grid-cols-2">
        <Card title="Matched requirements">
          <Tags items={match.matched} tone="green" empty="No clear matches found." />
        </Card>
        <Card title="Gaps to address">
          <Tags items={match.gaps} tone="amber" empty="No major gaps — nice." />
        </Card>
      </div>

      <Card title="Job requirements">
        <div className="space-y-3 text-sm">
          <Line label="Seniority" value={analysis.seniority || "—"} />
          <div>
            <p className="mb-1 font-medium text-slate-700">Required skills</p>
            <Tags items={analysis.required_skills} tone="slate" empty="—" />
          </div>
          <div>
            <p className="mb-1 font-medium text-slate-700">Keywords</p>
            <Tags items={analysis.keywords} tone="slate" empty="—" />
          </div>
        </div>
      </Card>

      <Card title="Tailored bullets">
        {tailored.bullets.length === 0 ? (
          <p className="text-sm text-slate-500">No bullets were rewritten.</p>
        ) : (
          <div className="space-y-4">
            {tailored.bullets.map((b, i) => (
              <div key={i} className="grid gap-2 md:grid-cols-2">
                <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-500">
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide">Original</p>
                  {b.original}
                </div>
                <div className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-slate-800">
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-green-700">Rewritten</p>
                  {b.rewritten}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </section>
  );
}

function ScoreCard({ score, rationale }: { score: number; rationale: string }) {
  const tone = score >= 75 ? "text-green-600" : score >= 50 ? "text-amber-600" : "text-red-600";
  return (
    <div className="flex flex-col items-start gap-4 rounded-lg border border-slate-200 bg-white p-6 sm:flex-row sm:items-center">
      <div className="flex flex-col items-center">
        <span className={`text-5xl font-bold ${tone}`}>{score}</span>
        <span className="text-xs uppercase tracking-wide text-slate-400">match</span>
      </div>
      <p className="text-sm text-slate-600">{rationale}</p>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</h2>
      {children}
    </div>
  );
}

function Line({ label, value }: { label: string; value: string }) {
  return (
    <p>
      <span className="font-medium text-slate-700">{label}:</span> {value}
    </p>
  );
}

function Tags({
  items,
  tone,
  empty,
}: {
  items: string[];
  tone: "green" | "amber" | "slate";
  empty: string;
}) {
  const styles = {
    green: "bg-green-100 text-green-800",
    amber: "bg-amber-100 text-amber-800",
    slate: "bg-slate-100 text-slate-700",
  }[tone];

  if (items.length === 0) return <p className="text-sm text-slate-400">{empty}</p>;

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((it, i) => (
        <span key={i} className={`rounded-full px-3 py-1 text-xs font-medium ${styles}`}>
          {it}
        </span>
      ))}
    </div>
  );
}

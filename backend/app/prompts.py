"""Prompt templates, one per task. Kept in a single module for the MVP; when the
LangGraph refactor lands, each of these becomes an agent's instruction."""


def analyze_prompt(jd_text: str) -> str:
    return (
        "Analyze the following job description. Extract the required skills, "
        "nice-to-have skills, the seniority level (e.g. Intern, Junior, Mid, Senior), "
        "important ATS keywords, and the core responsibilities.\n\n"
        f"JOB DESCRIPTION:\n{jd_text}"
    )


def match_prompt(jd_text: str, resume_text: str) -> str:
    return (
        "Compare the candidate's resume against the job description.\n"
        "- matched: the JOB'S requirements/skills the resume clearly demonstrates. Phrase each "
        "as the requirement itself, as a SHORT skill phrase of a few words (e.g. 'React & TypeScript', "
        "'Scalable system design', 'REST APIs'). Do NOT copy full resume bullet sentences.\n"
        "- gaps: the job's requirements the resume does NOT evidence — same short-phrase style.\n"
        "- match_score: overall fit from 0-100.\n"
        "- rationale: one or two sentences.\n"
        "Both matched and gaps must be concise requirement phrases, never full sentences copied "
        "from the resume or the job description.\n\n"
        f"JOB DESCRIPTION:\n{jd_text}\n\n"
        f"RESUME:\n{resume_text}"
    )


def latex_prompt(
    resume_text: str,
    jd_text: str,
    keywords: list[str],
    tailored: list,
    macro_guide: str,
) -> str:
    tailored_txt = "\n".join(
        f"- ORIGINAL: {b.original}\n  REWRITE: {b.rewritten}" for b in tailored
    ) or "(none)"
    kw = ", ".join(keywords) or "(none)"
    jd = jd_text.strip() or "(no job description provided — do a general polish)"
    return (
        "Format this candidate's resume as the BODY of a LaTeX document using the fixed "
        "template macros described below, tailored to the TARGET JOB.\n\n"
        "ONE-PAGE / LENGTH RULE:\n"
        "- KEEP ALL of the candidate's sections and every bullet from the original resume. Do NOT drop, "
        "merge, cap, or summarize items — preserve every distinct point (including ALL coding stats: "
        "Codeforces rating, LeetCode rating, problems-solved counts, contest ranks).\n"
        "- Each original bullet belongs to EXACTLY ONE section — keep it in the SAME section the original "
        "put it in. NEVER repeat the same item in two sections (e.g. Experience items must not also appear "
        "under Achievements, and vice-versa).\n"
        "- Fit one page by being CONCISE per bullet (~1-2 lines, no padding), NOT by removing content.\n"
        "- Do NOT add new bullets beyond what the original resume contains.\n\n"
        "TAILORING (MAXIMUM, DOMAIN-ALIGNED — make it read like a strong fit for THIS job):\n"
        "- Aggressively rewrite EVERY bullet. It should look clearly DIFFERENT and more targeted than the "
        "original wording — do NOT merely copy or lightly tweak.\n"
        "- Reframe each project and bullet using the target job's DOMAIN language and terminology (e.g. if "
        "the job is payments/fintech, describe the candidate's platforms in transaction/payment/settlement/"
        "reliability terms). Draw the strongest possible parallel to the job's domain.\n"
        "- Lead each bullet with a strong action verb and the OUTCOME this job values; inject the job's "
        "keywords, technologies, and responsibilities heavily and naturally.\n"
        "- CRITICAL: do NOT tack the SAME phrase onto multiple bullets (e.g. repeating '...which can be "
        "applied to optimize payment operations'). That reads as keyword-stuffing. Instead, WEAVE the "
        "domain language INTO the middle of each bullet and VARY the wording every time. Each bullet must "
        "read as a distinct, natural sentence a human wrote, ~1-2 lines, no trailing filler clause.\n"
        "- REORDER for impact: put the most job-relevant project first; within each entry put the most "
        "relevant bullet first; reorder the skills list so job-required skills appear first.\n"
        "- Emphasize scale, reliability, and metrics where the candidate already has numbers.\n"
        "- Prefer any REWRITE wording provided below.\n\n"
        "FACTUAL FLOOR (the only hard limits):\n"
        "- Keep the real name, contact links, institutions, degrees, dates, CGPA, project names, and tech "
        "stacks intact. Do NOT invent employers, job titles, degrees, or numeric metrics that do not exist "
        "in the source. Reframing WHAT a project is about is allowed; fabricating fake jobs or fake numbers is not.\n"
        "OUTPUT RULES:\n"
        "- Output ONLY the document body (what goes between \\begin{document} and \\end{document}).\n"
        "- Do NOT output \\documentclass, \\usepackage, \\begin{document}, or \\end{document}.\n"
        "- Use ONLY the macros below. Escape LaTeX specials (% & _ # $) in the candidate's text.\n"
        "- No markdown fences, no commentary.\n\n"
        f"AVAILABLE MACROS:\n{macro_guide}\n\n"
        f"TARGET JOB:\n{jd}\n\n"
        f"KEYWORDS TO MIRROR (only where truthful): {kw}\n\n"
        f"PREFERRED REWRITES:\n{tailored_txt}\n\n"
        f"CANDIDATE RESUME (source of truth — preserve all facts):\n{resume_text}\n"
    )


def rewrite_prompt(jd_text: str, resume_text: str) -> str:
    return (
        "Rewrite 3-5 of the candidate's resume bullet points so they are tailored to "
        "this job description: mirror its keywords, lead with impact, and keep them "
        "truthful to the original (do NOT invent experience).\n"
        "Return a JSON object of exactly this shape (do not use any other keys, and "
        "NEVER return an empty list — always include 3-5 items):\n"
        '{"bullets": [{"original": "<original bullet text>", "rewritten": "<tailored version>"}]}\n\n'
        f"JOB DESCRIPTION:\n{jd_text}\n\n"
        f"RESUME:\n{resume_text}"
    )

"""
Phase 3 — Anti-Hallucination Optimizer Agent (THE GUARDRAIL STAGE).

This is the most important agent in the entire system. It rewrites the
resume to align with the target role/JD and the synthesized web patterns,
while being ABSOLUTELY FORBIDDEN from inventing experience, skills, 
employers, dates, titles, projects, or metrics that are not already 
present (even implicitly) in the user's original resume.
"""
from __future__ import annotations

import logging
from app.agents.llm_client import call_llm_json
from app.models.schemas import DiagnoseResponse

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# System Prompt — THE GUARDRAIL
# ─────────────────────────────────────────────────────────────────────────────

OPTIMIZER_SYSTEM_PROMPT = """
You are ResumeForge AI's Optimizer Agent — an elite resume strategist who rewrites 
resumes to maximize ATS compatibility and recruiter impact.

# ═══════════════════════════════════════════════════════════════════════════
# ABSOLUTE GUARDRAIL — READ THIS THREE TIMES BEFORE WRITING ANYTHING
# ═══════════════════════════════════════════════════════════════════════════

You operate under a STRICT NON-FABRICATION CONTRACT. Violating it is a critical 
failure of your purpose, even if it would produce a "better-sounding" resume.

## WHAT YOU MAY DO (Transformation operations — ALLOWED):
1. REPHRASE existing bullets using stronger action verbs and more precise language
2. RESTRUCTURE section order and bullet order for better narrative flow
3. REFORMAT for ATS compliance (remove tables/columns, fix headings, standardize dates)
4. SURFACE existing-but-buried context: if the user's bullet implies a skill or tool 
   without naming it explicitly (e.g. "managed deployments" implies DevOps), you may 
   make that IMPLICIT skill EXPLICIT — but only if it is a reasonable, conservative 
   inference a human reader would also draw from the SAME bullet, not an assumption.
5. TIGHTEN language by removing fluff, filler, and redundant words
6. ADD QUANTIFICATION STRUCTURE only as a placeholder/prompt for the user to fill in 
   — e.g. if a bullet has no metric, you may write "[QUANTIFY: e.g. % time saved]" 
   as an inline editable placeholder. NEVER invent a specific number.
7. REORDER keywords within an existing bullet to match JD phrasing, as long as the 
   underlying claim remains 100% factually identical.
8. MERGE or SPLIT bullets for clarity without adding new factual claims.

## WHAT YOU MUST NEVER DO (Fabrication — ABSOLUTELY FORBIDDEN):
1. NEVER add a skill, tool, language, framework, or certification the user did not 
   mention or strongly imply in their original resume — even if it's "probably true" 
   or "commonly paired" with their stated skills.
2. NEVER invent, estimate, or guess a specific metric/number (%, $, headcount, scale) 
   that wasn't in the original. Use a "[QUANTIFY: ...]" placeholder instead.
3. NEVER add a new job, project, employer, title, or date range that wasn't in the 
   original resume.
4. NEVER change a job title to a more senior-sounding one (e.g. "Junior Developer" 
   → "Software Engineer II") unless the original resume itself shows that title.
5. NEVER add education, degrees, or certifications not already listed.
6. NEVER copy phrases, structures, or content from the "web pattern profile" that 
   contain specific facts — only use it for STYLE and KEYWORD VOCABULARY inspiration.
7. NEVER claim the candidate has "led a team of X" or similar leadership/scale claims 
   unless explicitly stated in the original.
8. If you are EVER uncertain whether an addition counts as a reasonable inference vs. 
   fabrication, DEFAULT TO NOT ADDING IT. When in doubt, leave it out.

## SELF-CHECK BEFORE FINALIZING (perform this internally before output)
For every single change you make, ask: "Could I point to the EXACT phrase in the 
original resume that justifies this change?" If no, REVERT that change.

# ═══════════════════════════════════════════════════════════════════════════
# YOUR TASK
# ═══════════════════════════════════════════════════════════════════════════

You will receive:
1. The original resume text
2. The target role and optional job description
3. The Phase 1 diagnostic report (flaws, fluffy phrases, must-have keywords)
4. A synthesized "web pattern profile" (anonymized structural/style patterns — 
   STYLE INSPIRATION ONLY, never factual content)

Produce an optimized version of the resume that:
- Fixes every flaw flagged in the diagnostic where fixable through rephrasing/reformatting
- Removes fluffy phrases identified in the diagnostic
- Naturally incorporates must-have keywords WHERE the underlying experience already 
  supports them (skip any must-have keyword that has zero basis in the original resume 
  — instead, flag it for the skill gap plan)
- Matches the section ordering and stylistic conventions from the web pattern profile
- Uses power verbs from the pattern profile where they accurately describe the 
  candidate's existing actions
- Inserts "[QUANTIFY: ...]" placeholders anywhere impact would benefit from a metric 
  the original didn't provide

## OUTPUT CONTRACT
Respond with ONLY a valid JSON object. No markdown, no preamble.

{
  "optimized_text": "<the full rewritten resume as plain text with line breaks, 
                      ready for ATS parsing — preserve section headings>",
  "changes_summary": "<3-5 sentence summary of the categories of changes made>",
  "guardrail_audit": [
    {
      "change": "<short description of a specific change>",
      "justification": "<the exact original phrase/concept that justifies it>"
    }
  ],
  "keywords_incorporated": ["<keyword from must_haves that WAS naturally incorporated>"],
  "keywords_skipped_no_basis": ["<keyword from must_haves that had NO basis in original 
                                  resume and was correctly NOT added>"],
  "projected_ats_score": {
    "overall": <int 0-100>,
    "keyword_match": <int 0-100>,
    "formatting": <int 0-100>,
    "sections_completeness": <int 0-100>,
    "readability": <int 0-100>
  }
}
""".strip()


def run_optimizer(
    raw_text: str,
    target_role: str,
    job_description: str | None,
    diagnosis: DiagnoseResponse,
    pattern_profile: dict,
) -> dict:
    """
    Run the guardrailed optimizer agent.
    Returns the parsed JSON dict (validated/typed downstream by the caller).
    """
    jd_block = (
        f"\n\n## TARGET JOB DESCRIPTION\n{job_description.strip()}"
        if job_description
        else ""
    )

    must_haves_block = "\n".join(
        f"- {m.keyword}: {m.reason}" for m in diagnosis.must_haves
    ) or "(none identified)"

    fluffy_block = "\n".join(f"- {p}" for p in diagnosis.content_analysis.fluffy_phrases) or "(none identified)"

    flaws_block = "\n".join(
        f"- [{f.severity}] {f.type} at {f.location}: {f.description} → Fix: {f.suggestion}"
        for f in diagnosis.flaws
    ) or "(none identified)"

    user_prompt = f"""
## TARGET ROLE
{target_role}
{jd_block}

## ORIGINAL RESUME TEXT (the ONLY source of truth for facts)
---
{raw_text}
---

## PHASE 1 DIAGNOSTIC FINDINGS

### Flaws to fix:
{flaws_block}

### Fluffy phrases to remove:
{fluffy_block}

### Must-have keywords for this role (incorporate ONLY if supported by original text):
{must_haves_block}

## WEB PATTERN PROFILE (style/structure inspiration ONLY — never factual content)
{pattern_profile}

Now produce the guardrailed, optimized rewrite. Remember: every change must be 
traceable to something already in the original resume. Return ONLY the JSON object.
""".strip()

    logger.info("Running optimizer agent for role: %s", target_role)
    result = call_llm_json(OPTIMIZER_SYSTEM_PROMPT, user_prompt)

    # Lightweight runtime guardrail sanity check — log if audit trail missing
    if not result.get("guardrail_audit"):
        logger.warning("Optimizer returned no guardrail_audit trail — review output carefully")

    return result

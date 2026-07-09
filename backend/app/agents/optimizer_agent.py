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
   mention or strongly imply in their original resume.
2. NEVER invent, estimate, or guess a specific metric/number (%, $, headcount, scale) 
   that wasn't in the original. Use a "[QUANTIFY: ...]" placeholder instead.
3. NEVER add a new job, project, employer, title, or date range that wasn't in the 
   original resume.
4. NEVER change a job title to a more senior-sounding one unless the original shows it.
5. NEVER add education, degrees, or certifications not already listed.
6. NEVER copy specific facts from the web pattern profile — style inspiration only.
7. NEVER claim leadership/scale the candidate didn't explicitly state.
8. When in doubt, leave it out.

## SELF-CHECK BEFORE FINALIZING
For every change: "Could I point to the EXACT phrase in the original resume that 
justifies this?" If no, REVERT that change.

# ═══════════════════════════════════════════════════════════════════════════
# SCORING RULES FOR projected_ats_score — CRITICAL
# ═══════════════════════════════════════════════════════════════════════════
- Your projected scores represent IMPROVEMENT over the original scores provided
- If you fixed formatting flaws → formatting score MUST go up
- If you added/surfaced keywords → keyword_match MUST go up
- If you removed fluffy phrases → readability MUST go up
- The overall score MUST be >= the original overall score
- Realistic improvement range: +3 to +15 points overall
- Do NOT fabricate a massive jump — be honest and realistic

## OUTPUT CONTRACT
Respond with ONLY a valid JSON object. No markdown, no preamble.

{
  "optimized_text": "<the full rewritten resume as plain text with line breaks>",
  "changes_summary": "<3-5 sentence summary of the categories of changes made>",
  "guardrail_audit": [
    {
      "change": "<short description of a specific change>",
      "justification": "<the exact original phrase/concept that justifies it>"
    }
  ],
  "keywords_incorporated": ["<keyword from must_haves that WAS naturally incorporated>"],
  "keywords_skipped_no_basis": ["<keyword from must_haves that had NO basis in original>"],
  "projected_ats_score": {
    "overall": <int 0-100, MUST be >= original overall score>,
    "keyword_match": <int 0-100, MUST be >= original if keywords were added>,
    "formatting": <int 0-100, MUST be >= original if formatting was fixed>,
    "sections_completeness": <int 0-100>,
    "readability": <int 0-100, MUST be >= original if fluff was removed>
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
    jd_block = (
        f"\n\n## TARGET JOB DESCRIPTION\n{job_description.strip()}"
        if job_description
        else ""
    )

    must_haves_block = "\n".join(
        f"- {m.keyword}: {m.reason}" for m in diagnosis.must_haves
    ) or "(none identified)"

    fluffy_block = "\n".join(
        f"- {p}" for p in diagnosis.content_analysis.fluffy_phrases
    ) or "(none identified)"

    flaws_block = "\n".join(
        f"- [{f.severity}] {f.type} at {f.location}: {f.description} → Fix: {f.suggestion}"
        for f in diagnosis.flaws
    ) or "(none identified)"

    user_prompt = f"""
## TARGET ROLE
{target_role}
{jd_block}

## ORIGINAL ATS SCORES (Phase 1 diagnostic — your projected scores MUST be higher)
- Overall: {diagnosis.ats_score.overall}/100
- Keyword Match: {diagnosis.ats_score.keyword_match}/100
- Formatting: {diagnosis.ats_score.formatting}/100
- Sections Completeness: {diagnosis.ats_score.sections_completeness}/100
- Readability: {diagnosis.ats_score.readability}/100

CRITICAL: Your projected_ats_score overall MUST be >= {diagnosis.ats_score.overall}.
Score each dimension higher than the original where you made improvements.
Realistic improvement range is +3 to +15 points overall.

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

Now produce the guardrailed, optimized rewrite. Every change must be traceable to 
something already in the original resume. Return ONLY the JSON object.
""".strip()

    logger.info("Running optimizer agent for role: %s", target_role)
    result = call_llm_json(OPTIMIZER_SYSTEM_PROMPT, user_prompt)

    # Runtime safety net: never let projected score drop below original
    if "projected_ats_score" in result:
        original_overall = diagnosis.ats_score.overall
        projected_overall = result["projected_ats_score"].get("overall", original_overall)
        if projected_overall < original_overall:
            logger.warning(
                "Optimizer projected score (%d) below original (%d) — correcting",
                projected_overall,
                original_overall,
            )
            result["projected_ats_score"]["overall"] = original_overall

    if not result.get("guardrail_audit"):
        logger.warning("Optimizer returned no guardrail_audit trail — review output carefully")

    return result
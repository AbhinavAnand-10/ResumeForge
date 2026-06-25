"""
Phase 1 — Diagnostic Agent.

Sends the raw resume text + target role/JD to the LLM and receives a
structured JSON diagnostic report covering ATS scores, flaws, content
analysis, and missing must-have keywords.
"""
from __future__ import annotations

import logging
from app.agents.llm_client import call_llm_json
from app.models.schemas import (
    DiagnoseResponse,
    ATSScore,
    FlawItem,
    ContentAnalysis,
    MustHave,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# System Prompt (highly engineered)
# ─────────────────────────────────────────────────────────────────────────────

DIAGNOSTIC_SYSTEM_PROMPT = """
You are ResumeForge AI's Diagnostic Engine — a world-class ATS (Applicant Tracking System) 
specialist and senior technical recruiter with 20+ years of experience screening resumes for 
top-tier technology companies including FAANG, unicorn startups, and Fortune 500 firms.

## YOUR MISSION
Perform a brutally honest, exhaustive diagnostic analysis of the provided resume against the 
target role and optional job description. You are NOT here to be nice. You are here to give 
the candidate the exact honest assessment a top recruiter would never say to their face but 
absolutely thinks internally.

## SCORING RUBRIC
Score each dimension 0–100:
- keyword_match: How well does the resume vocabulary match the role/JD terminology?
- formatting: Is it ATS-parseable? Single column, standard fonts, no tables/graphics, 
  correct section headings, consistent date formats?
- sections_completeness: Are all critical sections present (Summary, Experience, Education, 
  Skills, and role-specific sections)?
- readability: Are bullet points concise, action-verb-led, and quantified where possible?
- overall: Weighted average. Weight: keyword_match×0.35, formatting×0.25, 
  sections_completeness×0.20, readability×0.20

## FLAW SEVERITY DEFINITIONS
- critical: Will cause immediate ATS rejection or recruiter discard
- moderate: Significantly weakens the application
- minor: Polish issues that reduce impact

## FLUFFY PHRASES (ALWAYS flag these as weak)
"Hardworking", "Team player", "Passionate", "Detail-oriented", "Fast learner", 
"Results-driven", "Dynamic", "Synergy", "Go-getter", "Think outside the box",
"Strong communication skills", "Proven track record" (without evidence), 
"Excellent problem solver", "Strategic thinker"

## OUTPUT CONTRACT
You MUST respond with ONLY a valid JSON object matching this exact schema. No markdown. 
No preamble. No explanation outside the JSON.

{
  "ats_score": {
    "overall": <int 0-100>,
    "keyword_match": <int 0-100>,
    "formatting": <int 0-100>,
    "sections_completeness": <int 0-100>,
    "readability": <int 0-100>
  },
  "flaws": [
    {
      "type": "<typo|formatting|missing_section|weak_verb|fluff|quantification_missing|ats_incompatible>",
      "severity": "<critical|moderate|minor>",
      "location": "<specific location in resume>",
      "description": "<what the problem is>",
      "suggestion": "<exactly how to fix it>"
    }
  ],
  "content_analysis": {
    "strong_points": ["<strength 1>", ...],
    "weak_points": ["<weakness 1>", ...],
    "fluffy_phrases": ["<exact phrase from resume>", ...],
    "unnecessary_sections": ["<section name>", ...]
  },
  "must_haves": [
    {
      "keyword": "<missing keyword/skill/tool>",
      "reason": "<why this is critical for the role>",
      "example_usage": "<how to incorporate it naturally if they have the experience>"
    }
  ],
  "jd_alignment_percent": <int 0-100 or null if no JD provided>,
  "summary": "<2-3 sentence honest executive summary of the resume's biggest strengths and weakest points>"
}
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# Agent function
# ─────────────────────────────────────────────────────────────────────────────

def run_diagnostic(
    session_id: str,
    raw_text: str,
    target_role: str,
    job_description: str | None,
) -> DiagnoseResponse:
    """
    Run the diagnostic agent and return a typed DiagnoseResponse.
    """
    jd_section = (
        f"\n\n## TARGET JOB DESCRIPTION\n{job_description.strip()}"
        if job_description
        else "\n\n(No specific job description provided — analyze for general suitability for the target role.)"
    )

    user_prompt = f"""
## TARGET ROLE
{target_role}
{jd_section}

## RESUME TEXT TO DIAGNOSE
---
{raw_text}
---

Perform the full diagnostic now. Return ONLY the JSON object.
""".strip()

    logger.info("[%s] Running diagnostic for role: %s", session_id, target_role)
    data = call_llm_json(DIAGNOSTIC_SYSTEM_PROMPT, user_prompt)

    # ── Parse into typed models ───────────────────────────────────────────────
    ats = ATSScore(**data["ats_score"])

    flaws = [FlawItem(**f) for f in data.get("flaws", [])]

    ca_raw = data.get("content_analysis", {})
    content_analysis = ContentAnalysis(
        strong_points=ca_raw.get("strong_points", []),
        weak_points=ca_raw.get("weak_points", []),
        fluffy_phrases=ca_raw.get("fluffy_phrases", []),
        unnecessary_sections=ca_raw.get("unnecessary_sections", []),
    )

    must_haves = [MustHave(**m) for m in data.get("must_haves", [])]

    return DiagnoseResponse(
        session_id=session_id,
        ats_score=ats,
        flaws=flaws,
        content_analysis=content_analysis,
        must_haves=must_haves,
        jd_alignment_percent=data.get("jd_alignment_percent"),
        summary=data.get("summary", ""),
    )

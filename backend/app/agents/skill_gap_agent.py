"""
Phase 4 — Skill Gap Closure Plan Agent.

Generates a legitimate, actionable roadmap of real-world projects,
certifications, and skills the user should acquire to actually close
the gaps identified in diagnosis — NOT a way to fake having them.
"""
from __future__ import annotations

import logging
from app.agents.llm_client import call_llm_json
from app.models.schemas import DiagnoseResponse, SkillGapItem

logger = logging.getLogger(__name__)

SKILL_GAP_SYSTEM_PROMPT = """
You are ResumeForge AI's Career Development Strategist. Your job is to convert 
identified skill/keyword gaps into a concrete, legitimate action plan for the 
candidate to ACTUALLY acquire the missing capabilities — never to suggest 
exaggerating or fabricating experience on the resume.

## YOUR MISSION
For every must-have keyword/skill that was flagged as having "no basis" in the 
original resume (meaning the optimizer correctly did NOT add it), produce a 
real, achievable plan to close that gap legitimately.

## GUIDANCE FOR GOOD RECOMMENDATIONS
- Prefer free or low-cost, reputable resources (official docs, freeCodeCamp, 
  Coursera audit mode, YouTube courses from credible channels, official 
  certification bodies) over expensive bootcamps unless warranted
- Suggest a CONCRETE project idea, not just "learn X" — something they could 
  build in the estimated time and then legitimately add to their resume
- Be realistic about time estimates
- Prioritize: "high" = blocking for most applications to this role, 
  "medium" = strongly preferred, "low" = nice-to-have differentiator

## OUTPUT CONTRACT
Respond with ONLY a valid JSON object. No markdown, no preamble.

{
  "skill_gap_plan": [
    {
      "skill": "<the missing skill/keyword>",
      "priority": "<high|medium|low>",
      "suggested_action": "<concrete project or learning action>",
      "resources": ["<specific resource name/type>", ...],
      "estimated_time": "<e.g. '2-3 weekends' or '4-6 weeks part-time'>"
    }
  ]
}
""".strip()


def generate_skill_gap_plan(
    target_role: str,
    diagnosis: DiagnoseResponse,
    keywords_skipped_no_basis: list[str],
) -> list[SkillGapItem]:
    """
    Generate the skill gap closure plan based on keywords that genuinely
    could not be incorporated into the resume (no basis in original text).
    """
    if not keywords_skipped_no_basis:
        logger.info("No skill gaps to plan for — all must-haves had basis in resume")
        return []

    gaps_block = "\n".join(f"- {kw}" for kw in keywords_skipped_no_basis)

    user_prompt = f"""
## TARGET ROLE
{target_role}

## GENUINE SKILL GAPS (no basis found in candidate's original resume)
{gaps_block}

## DIAGNOSTIC CONTEXT
Summary: {diagnosis.summary}

Generate the legitimate skill closure plan now. Return ONLY the JSON object.
""".strip()

    logger.info("Generating skill gap plan for %d gaps", len(keywords_skipped_no_basis))

    try:
        data = call_llm_json(SKILL_GAP_SYSTEM_PROMPT, user_prompt)
        return [SkillGapItem(**item) for item in data.get("skill_gap_plan", [])]
    except Exception as exc:
        logger.warning("Skill gap plan generation failed: %s", exc)
        return []

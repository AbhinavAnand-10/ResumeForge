"""
Phase 2 — Web-Scraper Synthesizer Agent.

Takes raw web search results (snippets of publicly accessible resumes/job
postings/career advice pages) and extracts ANONYMIZED structural and
linguistic patterns — never copies named individuals' personal data,
employers, or verbatim biographical content.
"""
from __future__ import annotations

import logging
from app.agents.llm_client import call_llm_json

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# System Prompt
# ─────────────────────────────────────────────────────────────────────────────

SYNTHESIZER_SYSTEM_PROMPT = """
You are ResumeForge AI's Pattern Synthesizer — an expert in resume linguistics, 
ATS keyword taxonomy, and recruiting trends. You are given raw web search snippets 
that may reference real resumes, job boards, or career-advice articles related to a 
target role.

## YOUR MISSION
Extract ONLY abstract, reusable PATTERNS from these snippets. You are building a 
"style and structure profile" for the target role — NOT a copy of anyone's resume.

## STRICT PRIVACY & IP RULES — NON-NEGOTIABLE
1. NEVER extract, output, or reference any named individual's name, employer, school, 
   email, phone number, LinkedIn URL, or any personally identifiable information.
2. NEVER quote or reproduce verbatim sentences, bullet points, or paragraphs from the 
   source material. Everything you output must be GENERALIZED and ABSTRACTED.
3. If a snippet appears to be paywalled, copyrighted long-form content, or a personal 
   blog narrative, IGNORE its specific wording — only note the general structural 
   pattern (e.g. "uses a 3-bullet achievement format" not the achievements themselves).
4. Your output describes PATTERNS ("strong resumes for this role tend to lead bullets 
   with metrics-driven action verbs like X, Y, Z") not INSTANCES ("John Smith's resume 
   says...").
5. If the search results are empty, low-quality, or contain nothing useful, say so 
   honestly in low_confidence_note — do NOT fabricate patterns to fill the schema.

## WHAT TO EXTRACT
- Common section ordering for this role (e.g. Summary → Skills → Experience → Projects)
- Frequently recurring action verbs and power words
- Keyword/tooling terminology density (technologies, methodologies, certifications 
  commonly mentioned for this role)
- Typical quantification patterns (e.g. "% improvement", "$ revenue impact", "# users")
- Common resume length / bullet density norms
- Industry-specific phrasing conventions

## OUTPUT CONTRACT
Respond with ONLY a valid JSON object. No markdown, no preamble.

{
  "section_ordering_pattern": ["<section>", "<section>", ...],
  "high_frequency_keywords": ["<keyword>", ...],
  "power_verbs": ["<verb>", ...],
  "quantification_patterns": ["<pattern description>", ...],
  "structural_norms": {
    "typical_bullet_count_per_role": "<e.g. '3-5 bullets per job'>",
    "typical_resume_length": "<e.g. '1 page for <5yrs experience'>",
    "common_formatting_notes": "<e.g. 'reverse-chronological, no photos'>"
  },
  "industry_phrasing_conventions": ["<convention>", ...],
  "sources_referenced_count": <int>,
  "low_confidence_note": "<string, empty if confidence is high>"
}
""".strip()


def synthesize_patterns(
    target_role: str,
    search_results: list[dict],
) -> dict:
    """
    Given raw web search results, extract anonymized structural patterns.
    Returns a dict (already-parsed JSON from the LLM).
    Falls back to an empty-but-valid pattern object if no search results exist.
    """
    if not search_results:
        logger.info("No search results available — returning neutral pattern baseline")
        return {
            "section_ordering_pattern": ["Summary", "Skills", "Experience", "Education", "Projects"],
            "high_frequency_keywords": [],
            "power_verbs": ["Led", "Built", "Designed", "Optimized", "Delivered", "Architected"],
            "quantification_patterns": ["% improvement", "$ impact", "# of users/scale"],
            "structural_norms": {
                "typical_bullet_count_per_role": "3-5 bullets per role",
                "typical_resume_length": "1 page for <7 years experience, 2 pages max",
                "common_formatting_notes": "reverse-chronological order, no tables/graphics/photos",
            },
            "industry_phrasing_conventions": [],
            "sources_referenced_count": 0,
            "low_confidence_note": "No web search results were available; using general ATS best-practice baseline instead of role-specific data.",
        }

    # Build a sanitized snippet block — only titles + truncated text, no raw URLs
    # passed into the prompt as identifying info beyond domain context.
    snippet_blocks = []
    for i, result in enumerate(search_results[:5], start=1):
        title = result.get("title", "")[:150]
        snippet = result.get("snippet", "")[:1200]
        snippet_blocks.append(f"### Source {i}\nTitle: {title}\nContent snippet: {snippet}")

    user_prompt = f"""
## TARGET ROLE
{target_role}

## RAW WEB SEARCH SNIPPETS (extract patterns only — do not quote verbatim)
{chr(10).join(snippet_blocks)}

Extract the abstracted pattern profile now. Return ONLY the JSON object.
""".strip()

    logger.info("Synthesizing patterns from %d search results for role: %s", len(search_results), target_role)

    try:
        return call_llm_json(SYNTHESIZER_SYSTEM_PROMPT, user_prompt)
    except Exception as exc:
        logger.warning("Pattern synthesis failed (%s); falling back to baseline", exc)
        return synthesize_patterns(target_role, [])  # recursive fallback to baseline

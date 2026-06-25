"""
POST /api/optimize

Orchestrates the full Phase 2-4 pipeline:
  1. Web search for accepted resumes for the target role
  2. Synthesize anonymized structural/style patterns from results
  3. Run the guardrailed optimizer agent to rewrite the resume
  4. Compute a structured diff between original and optimized text
  5. Generate the skill gap closure plan for any keywords that had no basis
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException

from app.services.web_search import search_accepted_resumes
from app.services.diff_engine import compute_diff
from app.agents.synthesizer_agent import synthesize_patterns
from app.agents.optimizer_agent import run_optimizer
from app.agents.skill_gap_agent import generate_skill_gap_plan
from app.models.schemas import OptimizeRequest, OptimizeResponse, ATSScore
from app.utils.session_store import session_store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_resume(request: OptimizeRequest):
    session = session_store.get(request.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-upload your resume.",
        )

    # ── Step 1: Web search for accepted resumes ────────────────────────────────
    try:
        search_results = await search_accepted_resumes(
            target_role=request.target_role,
        )
    except Exception as exc:
        logger.warning("[%s] Web search failed, continuing without it: %s", request.session_id, exc)
        search_results = []

    web_sources_used = [r["url"] for r in search_results if r.get("url")]

    # ── Step 2: Synthesize anonymized patterns ─────────────────────────────────
    pattern_profile = synthesize_patterns(
        target_role=request.target_role,
        search_results=search_results,
    )

    # ── Step 3: Run the guardrailed optimizer agent ─────────────────────────────
    try:
        opt_result = run_optimizer(
            raw_text=request.raw_text,
            target_role=request.target_role,
            job_description=request.job_description,
            diagnosis=request.diagnosis,
            pattern_profile=pattern_profile,
        )
    except ValueError as exc:
        logger.error("[%s] Optimizer LLM call failed: %s", request.session_id, exc)
        raise HTTPException(
            status_code=502,
            detail="The optimization AI did not return a valid response. Please try again.",
        ) from exc
    except Exception as exc:
        logger.exception("[%s] Unexpected optimizer error", request.session_id)
        raise HTTPException(status_code=500, detail="Optimization failed unexpectedly.") from exc

    optimized_text = opt_result.get("optimized_text", "")
    if not optimized_text.strip():
        raise HTTPException(status_code=502, detail="Optimizer returned empty content.")

    # ── Step 4: Structured diff ─────────────────────────────────────────────────
    diff_lines = compute_diff(request.raw_text, optimized_text)

    # ── Step 5: Skill gap closure plan ──────────────────────────────────────────
    keywords_skipped = opt_result.get("keywords_skipped_no_basis", [])
    skill_gap_plan = generate_skill_gap_plan(
        target_role=request.target_role,
        diagnosis=request.diagnosis,
        keywords_skipped_no_basis=keywords_skipped,
    )

    # ── Assemble response ───────────────────────────────────────────────────────
    projected_score = ATSScore(**opt_result["projected_ats_score"])
    score_delta = projected_score.overall - request.diagnosis.ats_score.overall

    response = OptimizeResponse(
        session_id=request.session_id,
        original_text=request.raw_text,
        optimized_text=optimized_text,
        diff_lines=diff_lines,
        projected_ats_score=projected_score,
        score_delta=score_delta,
        changes_summary=opt_result.get("changes_summary", ""),
        skill_gap_plan=skill_gap_plan,
        web_sources_used=web_sources_used,
    )

    session_store.update(request.session_id, {"optimized_text": optimized_text})

    logger.info(
        "[%s] Optimization complete. Score: %d -> %d (Δ%+d)",
        request.session_id,
        request.diagnosis.ats_score.overall,
        projected_score.overall,
        score_delta,
    )

    return response

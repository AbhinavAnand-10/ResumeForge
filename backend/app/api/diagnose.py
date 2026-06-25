"""
POST /api/diagnose

Runs the Phase 1 diagnostic agent against the uploaded resume text.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException

from app.agents.diagnostic_agent import run_diagnostic
from app.models.schemas import DiagnoseRequest, DiagnoseResponse
from app.utils.session_store import session_store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose_resume(request: DiagnoseRequest):
    session = session_store.get(request.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-upload your resume.",
        )

    try:
        diagnosis = run_diagnostic(
            session_id=request.session_id,
            raw_text=request.raw_text,
            target_role=request.target_role,
            job_description=request.job_description,
        )
    except ValueError as exc:
        logger.error("[%s] Diagnostic LLM call failed: %s", request.session_id, exc)
        raise HTTPException(
            status_code=502,
            detail="The diagnostic AI did not return a valid response. Please try again.",
        ) from exc
    except Exception as exc:
        logger.exception("[%s] Unexpected diagnostic error", request.session_id)
        raise HTTPException(status_code=500, detail="Diagnostic failed unexpectedly.") from exc

    # Persist the diagnosis for use in Phase 2/3
    session_store.update(request.session_id, {"diagnosis": diagnosis.model_dump()})

    return diagnosis

"""
POST /api/export

Generates a downloadable, ATS-compliant PDF or DOCX of the optimized resume.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Response

from app.services.export import generate_pdf, generate_docx
from app.models.schemas import ExportRequest
from app.utils.session_store import session_store

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/export")
async def export_resume(request: ExportRequest):
    session = session_store.get(request.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-upload your resume.",
        )

    if not request.optimized_text.strip():
        raise HTTPException(status_code=400, detail="optimized_text is empty.")

    safe_role = "".join(c if c.isalnum() else "_" for c in request.target_role)[:40]

    try:
        if request.format == "pdf":
            file_bytes = generate_pdf(request.optimized_text, request.target_role)
            media_type = "application/pdf"
            filename = f"ResumeForge_{safe_role}.pdf"
        else:
            file_bytes = generate_docx(request.optimized_text, request.target_role)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"ResumeForge_{safe_role}.docx"
    except RuntimeError as exc:
        logger.error("[%s] Export failed: %s", request.session_id, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    logger.info("[%s] Exported %s (%d bytes)", request.session_id, filename, len(file_bytes))

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

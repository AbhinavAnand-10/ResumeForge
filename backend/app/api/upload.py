"""
POST /api/upload

Receives a resume file (PDF/DOCX), target role, and optional job description.
Extracts raw text and stores it in the session store for subsequent phases.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.parser import parse_resume
from app.models.schemas import UploadResponse
from app.utils.session_store import session_store
from app.utils.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    job_description: str | None = Form(None),
):
    # ── Validate file type ────────────────────────────────────────────────────
    if not file.filename or not file.filename.lower().endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX file.",
        )

    # ── Validate file size ────────────────────────────────────────────────────
    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f}MB). Max size is {settings.max_file_size_mb}MB.",
        )

    if not target_role or not target_role.strip():
        raise HTTPException(status_code=400, detail="target_role is required.")

    # ── Parse ──────────────────────────────────────────────────────────────────
    try:
        raw_text, sections = parse_resume(file.filename, file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Could not extract meaningful text from the file. "
                   "It may be a scanned image — please upload a text-based PDF or DOCX.",
        )

    # ── Store session ─────────────────────────────────────────────────────────
    session_id = session_store.create({
        "filename": file.filename,
        "raw_text": raw_text,
        "target_role": target_role.strip(),
        "job_description": job_description.strip() if job_description else None,
    })

    logger.info("[%s] Uploaded %s (%d chars, sections: %s)", session_id, file.filename, len(raw_text), sections)

    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        raw_text=raw_text,
        word_count=len(raw_text.split()),
        char_count=len(raw_text),
        detected_sections=sections,
    )

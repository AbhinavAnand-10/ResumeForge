"""
Pydantic v2 schemas — single source of truth for every API contract.
"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Upload
# ─────────────────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    raw_text: str
    word_count: int
    char_count: int
    detected_sections: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# Diagnose
# ─────────────────────────────────────────────────────────────────────────────

class DiagnoseRequest(BaseModel):
    session_id: str
    raw_text: str
    target_role: str
    job_description: str | None = None


class ATSScore(BaseModel):
    overall: int = Field(..., ge=0, le=100, description="0-100 ATS compatibility score")
    keyword_match: int = Field(..., ge=0, le=100)
    formatting: int = Field(..., ge=0, le=100)
    sections_completeness: int = Field(..., ge=0, le=100)
    readability: int = Field(..., ge=0, le=100)


class FlawItem(BaseModel):
    type: str           # "typo" | "formatting" | "missing_section" | "weak_verb" | "fluff"
    severity: str       # "critical" | "moderate" | "minor"
    location: str       # e.g. "Experience section, bullet 3"
    description: str
    suggestion: str


class ContentAnalysis(BaseModel):
    strong_points: list[str]
    weak_points: list[str]
    fluffy_phrases: list[str]      # generic buzzwords to remove
    unnecessary_sections: list[str]


class MustHave(BaseModel):
    keyword: str
    reason: str
    example_usage: str


class DiagnoseResponse(BaseModel):
    session_id: str
    ats_score: ATSScore
    flaws: list[FlawItem]
    content_analysis: ContentAnalysis
    must_haves: list[MustHave]
    jd_alignment_percent: int | None = None
    summary: str


# ─────────────────────────────────────────────────────────────────────────────
# Optimize
# ─────────────────────────────────────────────────────────────────────────────

class OptimizeRequest(BaseModel):
    session_id: str
    raw_text: str
    target_role: str
    job_description: str | None = None
    diagnosis: DiagnoseResponse


class DiffLine(BaseModel):
    line_no: int
    original: str
    optimized: str
    change_type: str    # "unchanged" | "modified" | "added" | "removed"
    reason: str | None = None


class SkillGapItem(BaseModel):
    skill: str
    priority: str       # "high" | "medium" | "low"
    suggested_action: str
    resources: list[str]
    estimated_time: str


class OptimizeResponse(BaseModel):
    session_id: str
    original_text: str
    optimized_text: str
    diff_lines: list[DiffLine]
    projected_ats_score: ATSScore
    score_delta: int
    changes_summary: str
    skill_gap_plan: list[SkillGapItem]
    web_sources_used: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# Export
# ─────────────────────────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    session_id: str
    optimized_text: str
    target_role: str
    format: str = Field("pdf", pattern="^(pdf|docx)$")


# ─────────────────────────────────────────────────────────────────────────────
# Generic error wrapper
# ─────────────────────────────────────────────────────────────────────────────

class APIError(BaseModel):
    error: str
    detail: str | None = None
    code: str | None = None

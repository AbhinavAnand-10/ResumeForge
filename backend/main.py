"""
ResumeForge AI — FastAPI Backend Entrypoint.

Run locally:
    uvicorn main:app --reload --port 8000

Run in production:
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import upload, diagnose, optimize, export
from app.utils.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("resumeforge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ResumeForge AI backend starting up...")
    logger.info("LLM provider: %s | Search provider: %s", settings.llm_provider, settings.search_provider)
    if not settings.active_llm_api_key:
        logger.warning(
            "No API key set for the active LLM provider (%s). "
            "Diagnose/Optimize endpoints will fail until configured.",
            settings.llm_provider,
        )
    yield
    logger.info("ResumeForge AI backend shutting down.")


app = FastAPI(
    title="ResumeForge AI",
    description="AI-driven resume authentication and optimization platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request timing / logging middleware ─────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "%s %s -> %d (%.0fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ── Routes ───────────────────────────────────────────────────────────────────
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(diagnose.router, prefix="/api", tags=["diagnose"])
app.include_router(optimize.router, prefix="/api", tags=["optimize"])
app.include_router(export.router, prefix="/api", tags=["export"])


@app.get("/")
async def root():
    return {"app": "ResumeForge AI", "status": "running", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "search_provider": settings.search_provider,
        "llm_configured": bool(settings.active_llm_api_key),
    }

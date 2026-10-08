"""
CareerPilot AI - API Routes

FastAPI router with all HTTP endpoints.
"""

import asyncio
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import get_settings
from app.api.dependencies import limiter
from app.schemas.models import AnalysisResponse, HealthResponse, InterviewTurnRequest, InterviewTurnResponse, CompareResponse
from app.services.analysis_service import run_analysis, run_analysis_stream
from app.services.interview_service import handle_interview_turn
from app.services.compare_service import run_comparison
from app.tools.pdf_parser import extract_text_from_pdf

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _request_id(request: Request) -> str:
    """Extract request ID set by RequestIdMiddleware."""
    return request.scope.get("extensions", {}).get("request_id", str(uuid.uuid4()))


def _safe_error(request: Request, exc: Exception, public_msg: str) -> HTTPException:
    """
    Log the full exception server-side and return an HTTPException that contains
    only a generic message + request ID (never the raw exception text).
    """
    req_id = _request_id(request)
    logger.exception("[%s] %s: %s", req_id, public_msg, exc)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"message": public_msg, "request_id": req_id},
    )


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """Return service health status and configuration info."""
    s = get_settings()
    return HealthResponse(
        status="ok",
        version=s.version,
        llm_provider=s.llm_provider,
    )


@router.get(
    "/health/ready",
    summary="Readiness check — verifies API key is configured",
    tags=["System"],
)
async def health_ready():
    """
    Deeper health check. Verifies the LLM API key is present.
    Returns 200 if ready, 503 if not.
    No LLM call is made.
    """
    s = get_settings()
    key_present = bool(
        (s.llm_provider == "openai" and s.openai_api_key)
        or (s.llm_provider == "google" and s.google_api_key)
        or (s.llm_provider == "anthropic" and s.anthropic_api_key)
    )
    if not key_present:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "reason": f"No API key configured for provider '{s.llm_provider}'.",
            },
        )
    return {"status": "ready", "llm_provider": s.llm_provider, "version": s.version}


# ---------------------------------------------------------------------------
# Main Analysis Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Run career analysis",
    tags=["Analysis"],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def analyze_career(
    request: Request,
    cv_file: Annotated[UploadFile, File(description="Resume/CV in PDF format")],
    job_description: Annotated[
        str,
        # Single source of truth: FastAPI validates min/max here.
        # We do NOT duplicate this check in code below.
        Form(
            description="Full text of the job description",
            min_length=50,
            max_length=settings.max_jd_chars,
        ),
    ],
) -> AnalysisResponse:
    """
    Main analysis endpoint.

    Accepts a multipart/form-data request with:
    - cv_file: PDF file (≤ MAX_PDF_SIZE_MB)
    - job_description: text (50 – MAX_JD_CHARS characters)
    """
    req_id = _request_id(request)
    s = get_settings()
    max_bytes = s.max_pdf_size_mb * 1024 * 1024

    # ---- Validate file type ------------------------------------------------
    if not cv_file.filename or not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported. Please upload a .pdf file.",
        )

    # ---- Early size check via Content-Length header -----------------------
    # Reject before reading the body if the client declared a size.
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_bytes + 4096:  # +4096 for form overhead
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"PDF file exceeds maximum size of {s.max_pdf_size_mb}MB.",
        )

    # ---- Read upload in chunks with hard cap --------------------------------
    chunks = []
    total = 0
    while True:
        chunk = await cv_file.read(8192)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"PDF file exceeds maximum size of {s.max_pdf_size_mb}MB.",
            )
        chunks.append(chunk)
    content = b"".join(chunks)

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # ---- Run PDF parsing off the event loop (CPU-bound) --------------------
    logger.info("[%s] Extracting text from PDF (%d bytes)", req_id, len(content))
    try:
        resume_text = await asyncio.to_thread(
            extract_text_from_pdf,
            content,
            cv_file.filename or "resume.pdf",
            s.max_pdf_pages,
            s.max_resume_chars,
        )
    except ValueError as exc:
        # Known validation errors (not a PDF, no text, etc.) — safe to surface
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # ---- Run the analysis pipeline -----------------------------------------
    logger.info("[%s] Starting analysis pipeline. JD: %d chars", req_id, len(job_description))
    try:
        result = await run_analysis(
            resume_text=resume_text,
            job_description=job_description.strip(),
            request_id=req_id,
        )
    except Exception as exc:
        _safe_error(request, exc, "Analysis pipeline encountered an unexpected error.")

    if result.status == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": result.error_message or "Analysis failed.", "request_id": req_id},
        )

    return result


@router.post(
    "/analyze/stream",
    summary="Run career analysis with SSE streaming",
    tags=["Analysis"],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def analyze_career_stream(
    request: Request,
    cv_file: Annotated[UploadFile, File(description="Resume/CV in PDF format")],
    job_description: Annotated[
        str,
        Form(
            description="Full text of the job description",
            min_length=50,
            max_length=settings.max_jd_chars,
        ),
    ],
) -> StreamingResponse:
    """
    Streaming analysis endpoint using Server-Sent Events (SSE).
    """
    req_id = _request_id(request)
    s = get_settings()
    max_bytes = s.max_pdf_size_mb * 1024 * 1024

    if not cv_file.filename or not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported. Please upload a .pdf file.",
        )

    chunks = []
    total = 0
    while True:
        chunk = await cv_file.read(8192)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"PDF file exceeds maximum size of {s.max_pdf_size_mb}MB.",
            )
        chunks.append(chunk)
    content = b"".join(chunks)

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        resume_text = await asyncio.to_thread(
            extract_text_from_pdf,
            content,
            cv_file.filename or "resume.pdf",
            s.max_pdf_pages,
            s.max_resume_chars,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    return StreamingResponse(
        run_analysis_stream(resume_text, job_description.strip(), req_id),
        media_type="text/event-stream"
    )
# ---------------------------------------------------------------------------
# Phase 6: Interview and Compare Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/interview/turn",
    response_model=InterviewTurnResponse,
    summary="Evaluate an interview answer",
    tags=["Interview"],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def interview_turn(
    request: Request,
    payload: InterviewTurnRequest,
) -> InterviewTurnResponse:
    """
    Evaluate a candidate's answer to an interview question.
    """
    try:
        return await handle_interview_turn(payload)
    except Exception as exc:
        _safe_error(request, exc, "Failed to evaluate interview answer.")


@router.post(
    "/compare",
    response_model=CompareResponse,
    summary="Compare resume against multiple job descriptions",
    tags=["Analysis"],
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def compare_jobs(
    request: Request,
    cv_file: Annotated[UploadFile, File(description="Resume/CV in PDF format")],
    job_descriptions: Annotated[
        list[str],
        Form(description="List of job descriptions to compare against")
    ],
) -> CompareResponse:
    """
    Compare a resume against multiple job descriptions.
    """
    req_id = _request_id(request)
    s = get_settings()
    max_bytes = s.max_pdf_size_mb * 1024 * 1024

    if not cv_file.filename or not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported. Please upload a .pdf file.",
        )

    if len(job_descriptions) < 2 or len(job_descriptions) > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Must provide between 2 and 5 job descriptions.",
        )

    chunks = []
    total = 0
    while True:
        chunk = await cv_file.read(8192)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"PDF file exceeds maximum size of {s.max_pdf_size_mb}MB.",
            )
        chunks.append(chunk)
    content = b"".join(chunks)

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    logger.info("[%s] Extracting text from PDF for compare (%d bytes)", req_id, len(content))
    try:
        resume_text = await asyncio.to_thread(
            extract_text_from_pdf,
            content,
            cv_file.filename or "resume.pdf",
            s.max_pdf_pages,
            s.max_resume_chars,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    logger.info("[%s] Starting multi-job comparison", req_id)
    try:
        result = await run_comparison(resume_text, job_descriptions)
        return result
    except Exception as exc:
        _safe_error(request, exc, "Comparison failed.")

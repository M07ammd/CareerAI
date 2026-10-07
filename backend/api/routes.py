"""
CareerPilot AI - API Routes

FastAPI router with all HTTP endpoints.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from config import get_settings
from schemas.models import AnalysisResponse, AnalysisRequest, HealthResponse
from services.analysis_service import run_analysis
from tools.pdf_parser import extract_text_from_pdf

logger = logging.getLogger(__name__)

router = APIRouter()


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
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.version,
        llm_provider=settings.llm_provider,
    )


# ---------------------------------------------------------------------------
# Main Analysis Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Run career analysis",
    description=(
        "Upload a CV/resume PDF and provide a job description to get a complete "
        "AI-powered career analysis including skill matching, gap analysis, "
        "interview questions, and a personalised roadmap."
    ),
    tags=["Analysis"],
)
async def analyze_career(
    cv_file: Annotated[UploadFile, File(description="Resume/CV in PDF format")],
    job_description: Annotated[
        str,
        Form(description="Full text of the job description", min_length=50),
    ],
) -> AnalysisResponse:
    """
    Main analysis endpoint.

    Accepts a multipart/form-data request with:
    - cv_file: PDF file
    - job_description: text form field
    """
    settings = get_settings()

    # ---- Validate file type ------------------------------------------------
    if not cv_file.filename or not cv_file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported. Please upload a .pdf file.",
        )

    # ---- Validate file size ------------------------------------------------
    content = await cv_file.read()
    max_size = settings.max_pdf_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"PDF file exceeds maximum size of {settings.max_pdf_size_mb}MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # ---- Validate job description -------------------------------------------
    jd = job_description.strip()
    if len(jd) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is too short. Please provide a complete job description.",
        )

    # ---- Extract text from PDF ---------------------------------------------
    logger.info("[API] Extracting text from PDF: %s (%d bytes)", cv_file.filename, len(content))
    try:
        resume_text = extract_text_from_pdf(content, filename=cv_file.filename or "resume.pdf")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # ---- Run the analysis pipeline -----------------------------------------
    logger.info("[API] Starting analysis pipeline")
    result = await run_analysis(resume_text=resume_text, job_description=jd)

    if result.status == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error_message or "Analysis pipeline failed",
        )

    return result

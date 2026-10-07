"""
CareerPilot AI - Analysis Service

Orchestrates the LangGraph workflow for a complete career analysis.

Status semantics:
  "success"  - all agents ran and final_report is present
  "partial"  - critical agents succeeded, optional agents (interview/roadmap) may have failed
  "error"    - a critical agent (resume/job/skill) failed; no usable result
"""

from __future__ import annotations

import logging
from typing import Literal

from graph.graph import get_graph
from graph.state import get_initial_state
from schemas.models import AnalysisResponse

logger = logging.getLogger(__name__)

# Critical agents: if these fail, the entire result is unusable.
CRITICAL_STEPS = {"resume_agent", "job_agent", "skill_agent"}


async def run_analysis(
    resume_text: str,
    job_description: str,
    request_id: str = "unknown",
) -> AnalysisResponse:
    """
    Run the full CareerPilot AI analysis pipeline.

    Args:
        resume_text:     Extracted text from the candidate's PDF resume.
        job_description: Full text of the job description.
        request_id:      Request ID for log correlation (never returned to client).

    Returns:
        AnalysisResponse with all available structured results.
    """
    logger.info(
        "[%s] Starting analysis. Resume: %d chars | JD: %d chars",
        request_id, len(resume_text), len(job_description),
    )

    initial_state = get_initial_state(
        resume_text=resume_text,
        job_description=job_description,
    )

    graph = get_graph()

    try:
        final_state = await graph.ainvoke(initial_state)
    except Exception as exc:
        # Graph-level crash — log with request_id, return generic message
        logger.exception("[%s] Graph execution crashed: %s", request_id, exc)
        return AnalysisResponse(
            status="error",
            error_message="The analysis workflow encountered an unexpected internal error.",
            processing_steps=[],
        )

    completed = final_state.get("completed_steps", [])
    errors = final_state.get("errors", [])

    # Detect critical failures
    critical_failed = [
        e for e in errors
        if str(e.get("step", "")).replace("WorkflowStep.", "").lower() in CRITICAL_STEPS
    ]

    if critical_failed and not final_state.get("resume_analysis"):
        logger.warning(
            "[%s] Critical agent failure. Completed: %s", request_id, completed
        )
        return AnalysisResponse(
            status="error",
            error_message="A critical analysis step failed. Please check your CV and try again.",
            processing_steps=completed,
        )

    # Classify result: success if report present, partial otherwise
    has_report = final_state.get("final_report") is not None
    status_val: Literal["success", "partial", "error"] = "success" if has_report else "partial"

    # Collect warnings for optional agent failures
    warnings = []
    for err in errors:
        step = str(err.get("step", ""))
        if not any(c in step.lower() for c in CRITICAL_STEPS):
            warnings.append(f"{step} encountered an issue; this section may be incomplete.")

    logger.info(
        "[%s] Analysis complete. Status: %s | Steps: %s | Warnings: %d",
        request_id, status_val, completed, len(warnings),
    )

    return AnalysisResponse(
        status=status_val,
        resume_analysis=final_state.get("resume_analysis"),
        job_analysis=final_state.get("job_analysis"),
        skill_match=final_state.get("skill_match"),
        skill_gaps=final_state.get("skill_gaps"),
        interview_questions=final_state.get("interview_questions"),
        career_roadmap=final_state.get("career_roadmap"),
        final_report=final_state.get("final_report"),
        warnings=warnings,
        processing_steps=completed,
    )

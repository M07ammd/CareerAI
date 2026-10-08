"""
CareerPilot AI - Analysis Service

Orchestrates the LangGraph workflow for a complete career analysis.

Status semantics:
  "success"  - all agents ran and final_report is present
  "partial"  - critical agents succeeded; optional agents (interview/roadmap) may have failed
  "error"    - a critical agent (resume/job/skill) failed after retries exhausted
"""

from __future__ import annotations

import json
import logging
from typing import Literal

from app.graph.graph import get_graph
from app.graph.state import get_initial_state
from app.schemas.models import AnalysisResponse

logger = logging.getLogger(__name__)

# Critical agents: if any of these fail, the result is unusable.
CRITICAL_STEPS = frozenset({"resume_agent", "job_agent", "skill_agent"})

# Optional agents: failure yields a warning, not an error.
OPTIONAL_STEPS = frozenset({"interview_agent", "roadmap_agent", "gap_agent", "report_agent", "cv_suggestion_agent"})


def _normalise_step(step: str) -> str:
    """Convert WorkflowStep.RESUME_AGENT → resume_agent."""
    return step.replace("WorkflowStep.", "").lower()


def _readable_step(step: str) -> str:
    """Convert resume_agent → Resume Agent."""
    return _normalise_step(step).replace("_", " ").title()


async def run_analysis(
    resume_text: str,
    job_description: str,
    request_id: str = "unknown",
) -> AnalysisResponse:
    """
    Run the full CareerPilot AI analysis pipeline.

    Args:
        resume_text:     Extracted text from the candidate PDF resume.
        job_description: Full text of the job description.
        request_id:      Request ID for log correlation (never returned to client).

    Returns:
        AnalysisResponse with all available structured results.
    """
    logger.info(
        "[%s] Starting analysis. Resume: %d chars | JD: %d chars",
        request_id, len(resume_text), len(job_description),
    )

    initial_state = get_initial_state(resume_text=resume_text, job_description=job_description)
    graph = get_graph()

    try:
        final_state = await graph.ainvoke(initial_state)
    except Exception as exc:
        logger.exception("[%s] Graph execution crashed: %s", request_id, exc)
        return AnalysisResponse(
            status="error",
            error_message="The analysis workflow encountered an unexpected internal error.",
            processing_steps=[],
        )

    completed = final_state.get("completed_steps", [])
    errors = final_state.get("errors", [])

    # Classify errors as critical vs optional
    critical_failed: list[str] = []
    warnings: list[str] = []
    for err in errors:
        step = _normalise_step(str(err.get("step", "")))
        msg = str(err.get("error", "Unknown error"))
        if step in CRITICAL_STEPS:
            critical_failed.append(step)
        else:
            # Produce a human-readable warning without leaking internal details
            warnings.append(f"{_readable_step(step)}: this section may be incomplete.")

    # If any critical agent failed, return error — no partial data is useful
    if critical_failed:
        failed_names = ", ".join(_readable_step(s) for s in critical_failed)
        logger.warning("[%s] Critical agent(s) failed: %s", request_id, failed_names)
        return AnalysisResponse(
            status="error",
            error_message=f"A critical analysis step failed ({failed_names}). Please check your inputs and try again.",
            failed_step=critical_failed[0],
            processing_steps=[str(s) for s in completed],
        )

    # Success if final_report present, partial otherwise
    has_report = final_state.get("final_report") is not None
    status_val: Literal["success", "partial", "error"] = "success" if has_report else "partial"

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
        processing_steps=[str(s) for s in completed],
    )


async def run_analysis_stream(
    resume_text: str,
    job_description: str,
    request_id: str = "unknown",
):
    """
    Run the full CareerPilot AI analysis pipeline and yield SSE events.

    Event types:
      step_started    { node }
      step_completed  { node }
      warning         { node, message }
      result          { ... AnalysisResponse JSON ... }
      error           { message, request_id }
    """
    logger.info(
        "[%s] Starting streaming analysis. Resume: %d chars | JD: %d chars",
        request_id, len(resume_text), len(job_description),
    )

    initial_state = get_initial_state(resume_text=resume_text, job_description=job_description)
    graph = get_graph()

    def _sse(payload: dict) -> str:
        return f"data: {json.dumps(payload)}\n\n"

    try:
        async for chunk in graph.astream(initial_state, stream_mode="updates"):
            for node_name, updates in chunk.items():
                if "errors" in updates and updates["errors"]:
                    step = _normalise_step(str(updates["errors"][-1].get("step", node_name)))
                    if step in CRITICAL_STEPS:
                        # Critical failure — emit error event (no internal details)
                        yield _sse({
                            "type": "error",
                            "message": f"A critical step ({_readable_step(step)}) failed.",
                            "request_id": request_id,
                        })
                        return
                    else:
                        yield _sse({
                            "type": "warning",
                            "node": node_name,
                            "message": f"{_readable_step(step)}: this section may be incomplete.",
                        })
                else:
                    yield _sse({"type": "step_completed", "node": node_name})

        # Build final result
        final_result = await run_analysis(resume_text, job_description, request_id)
        yield _sse({"type": "result", **final_result.model_dump()})

    except Exception as exc:
        logger.exception("[%s] Streaming graph execution crashed: %s", request_id, exc)
        yield _sse({
            "type": "error",
            "message": "The analysis encountered an internal error.",
            "request_id": request_id,
        })
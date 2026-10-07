"""
CareerPilot AI - Analysis Service

Orchestrates the LangGraph workflow for a complete career analysis.
"""

from __future__ import annotations

import logging
from typing import Optional

from graph.graph import get_graph
from graph.state import get_initial_state
from schemas.models import (
    AnalysisResponse,
    CareerRoadmap,
    FinalReport,
    InterviewQuestions,
    JobAnalysis,
    ResumeAnalysis,
    SkillGaps,
    SkillMatch,
)

logger = logging.getLogger(__name__)


async def run_analysis(
    resume_text: str,
    job_description: str,
) -> AnalysisResponse:
    """
    Run the full CareerPilot AI analysis pipeline.

    Args:
        resume_text:      Extracted text from the candidate's PDF resume.
        job_description:  Full text of the job description.

    Returns:
        AnalysisResponse with all structured results populated.
    """
    logger.info(
        "[AnalysisService] Starting analysis. Resume: %d chars | JD: %d chars",
        len(resume_text),
        len(job_description),
    )

    # Initialise state
    initial_state = get_initial_state(
        resume_text=resume_text,
        job_description=job_description,
    )

    # Compile and run graph
    graph = get_graph()

    try:
        final_state = await graph.ainvoke(initial_state)
    except Exception as exc:
        logger.exception("[AnalysisService] Graph execution failed: %s", exc)
        return AnalysisResponse(
            status="error",
            error_message=f"Workflow execution failed: {exc}",
            processing_steps=["Workflow failed during execution"],
        )

    # Extract results from final state
    errors = final_state.get("errors", [])
    completed = final_state.get("completed_steps", [])
    processing_log = final_state.get("processing_log", [])

    if errors and not final_state.get("final_report"):
        # At least one agent failed and we have no final report
        error_messages = [e.get("error", "Unknown error") for e in errors]
        logger.warning("[AnalysisService] Completed with errors: %s", error_messages)
        return AnalysisResponse(
            status="partial",
            resume_analysis=final_state.get("resume_analysis"),
            job_analysis=final_state.get("job_analysis"),
            skill_match=final_state.get("skill_match"),
            skill_gaps=final_state.get("skill_gaps"),
            interview_questions=final_state.get("interview_questions"),
            career_roadmap=final_state.get("career_roadmap"),
            final_report=final_state.get("final_report"),
            error_message="; ".join(error_messages),
            processing_steps=completed,
        )

    logger.info(
        "[AnalysisService] Analysis complete. Steps: %s", completed
    )

    return AnalysisResponse(
        status="success",
        resume_analysis=final_state.get("resume_analysis"),
        job_analysis=final_state.get("job_analysis"),
        skill_match=final_state.get("skill_match"),
        skill_gaps=final_state.get("skill_gaps"),
        interview_questions=final_state.get("interview_questions"),
        career_roadmap=final_state.get("career_roadmap"),
        final_report=final_state.get("final_report"),
        processing_steps=completed,
    )

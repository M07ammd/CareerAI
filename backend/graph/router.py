"""
CareerPilot AI - Supervisor / Router

Controls which agent runs next and handles retry logic.
"""

from __future__ import annotations

import logging

from graph.state import CareerPilotState
from schemas.models import WorkflowStep

logger = logging.getLogger(__name__)

# Maximum retries per agent before we abort
MAX_RETRIES = 2


def determine_next_step(state: CareerPilotState) -> str:
    """Determine the next missing piece of analysis."""
    if state.get("resume_analysis") is None:
        return "resume_agent"
    if state.get("job_analysis") is None:
        return "job_agent"
    if state.get("skill_match") is None:
        return "skill_agent"
    if state.get("skill_gaps") is None:
        return "gap_agent"
    if state.get("interview_questions") is None:
        return "interview_agent"
    if state.get("career_roadmap") is None:
        return "roadmap_agent"
    if state.get("final_report") is None:
        return "report_agent"
    return "__end__"

def supervisor_router(state: CareerPilotState) -> str:
    """
    LangGraph conditional edge function.
    Reads state and returns the name of the next node to execute.
    """
    next_node = determine_next_step(state)
    
    if next_node == "__end__":
        logger.info("[Supervisor] All tasks complete. Routing to END")
        return "__end__"

    errors = state.get("errors", [])
    retry_counts = state.get("retry_counts", {})

    # Check for too many errors on the intended next step
    if errors:
        last_error = errors[-1]
        # Match node name to step name for error checking
        step_map = {
            "resume_agent": WorkflowStep.RESUME_AGENT,
            "job_agent": WorkflowStep.JOB_AGENT,
            "skill_agent": WorkflowStep.SKILL_AGENT,
            "gap_agent": WorkflowStep.GAP_AGENT,
            "interview_agent": WorkflowStep.INTERVIEW_AGENT,
            "roadmap_agent": WorkflowStep.ROADMAP_AGENT,
            "report_agent": WorkflowStep.REPORT_AGENT,
        }
        step_enum = step_map.get(next_node)
        
        if step_enum and last_error.get("step") == step_enum:
            retries = retry_counts.get(step_enum, 0)
            if retries >= MAX_RETRIES:
                logger.warning(
                    "[Supervisor] Step %s failed %d times. Aborting workflow.",
                    next_node, retries
                )
                return "__end__"
            logger.info(
                "[Supervisor] Step %s failed. Will retry (attempt %d/%d).",
                next_node, retries + 1, MAX_RETRIES
            )

    logger.info("[Supervisor] Routing to → %s", next_node)
    return next_node


def supervisor_node(state: CareerPilotState) -> dict:
    """
    Supervisor node that updates retry counts when a step has failed.
    """
    errors = state.get("errors", [])
    retry_counts = dict(state.get("retry_counts", {}))
    completed = state.get("completed_steps", [])
    
    next_node = determine_next_step(state)

    if errors:
        last_error = errors[-1]
        step = last_error.get("step")
        if step and step not in completed:
            retry_counts[step] = retry_counts.get(step, 0) + 1
            logger.info(
                "[Supervisor] Incremented retry count for %s → %d",
                step, retry_counts[step]
            )

    log_msg = f"Supervisor: completed={completed}, next={next_node}"
    logger.info("[Supervisor] %s", log_msg)

    return {
        "retry_counts": retry_counts,
        "processing_log": [log_msg],
    }

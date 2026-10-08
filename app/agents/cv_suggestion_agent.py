"""
CareerPilot AI - CV Suggestion Agent
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from app.agents.agent_runner import is_transient
from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.schemas.models import CVBulletRewrite, WorkflowStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a Senior Resume Writer and Career Coach.\n"
    "Identify the 3 weakest bullet points in the candidate's resume "
    "and rewrite them to better align with the job description. "
    "Make them more impactful, metric-driven, and include required keywords.\n"
    + ANTI_INJECTION_INSTRUCTION
)


class BulletRewrites(BaseModel):
    rewrites: list[CVBulletRewrite]


async def cv_suggestion_agent(state: CareerPilotState) -> dict:
    logger.info("[CVSuggestionAgent] Starting CV suggestion analysis")

    resume_analysis = state.get("resume_analysis")
    job_analysis = state.get("job_analysis")
    final_report = state.get("final_report")

    if not resume_analysis or not job_analysis or not final_report:
        logger.warning("[CVSuggestionAgent] Missing prerequisites, skipping")
        return {
            "errors": [
                {
                    "step": WorkflowStep.CV_SUGGESTION_AGENT,
                    "error": "Missing prerequisites",
                }
            ],
            "processing_log": ["CVSuggestionAgent FAILED: Missing prerequisites"],
        }

    resume_text = state.get("resume_text", "")
    job_desc = state.get("job_description", "")

    llm = get_structured_llm(BulletRewrites)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                wrap_user_content("CANDIDATE RESUME", resume_text)
                + "\n\n"
                + wrap_user_content("JOB DESCRIPTION", job_desc)
            )
        ),
    ]

    try:
        result: BulletRewrites = await llm.ainvoke(messages)
        # Mutate the existing report copy
        final_report = final_report.model_copy()
        final_report.cv_bullet_rewrites = result.rewrites

        logger.info(
            "[CVSuggestionAgent] Done. Rewrote %d bullets.", len(result.rewrites)
        )
        return {
            "final_report": final_report,
            "completed_steps": [WorkflowStep.CV_SUGGESTION_AGENT],
            "processing_log": [
                f"CVSuggestionAgent completed. Generated {len(result.rewrites)} rewrites."
            ],
        }
    except Exception as exc:
        if is_transient(exc):
            logger.warning("[CVSuggestionAgent] Transient error: %s", exc)
            raise
        logger.exception("[CVSuggestionAgent] Non-retryable error: %s", exc)
        return {
            "errors": [{"step": WorkflowStep.CV_SUGGESTION_AGENT, "error": str(exc)}],
            "processing_log": [f"CVSuggestionAgent FAILED: {exc}"],
        }

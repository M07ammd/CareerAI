"""
CareerPilot AI - Job Analysis Agent

Parses the job description and extracts structured requirements.
Transient LLM errors propagate for RetryPolicy; validation errors returned immediately.
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.agent_runner import is_transient
from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.schemas.models import JobAnalysis, WorkflowStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a Senior Technical Recruiter and Job Description Analyst.\n\n"
    "Your task is to carefully read a job description and extract structured information.\n\n"
    "Guidelines:\n"
    "- Separate required (must-have) skills from preferred (nice-to-have) skills.\n"
    "- Identify ALL technologies mentioned, even incidentally.\n"
    "- Determine the domain (e.g. ML Engineering, Backend, Data Science, Full Stack, DevOps).\n"
    "- Estimate the seniority level from job title and requirements.\n"
    "- If experience years are not explicitly stated, estimate from the responsibilities listed.\n"
    "- Extract concrete responsibilities, not vague phrases.\n"
    + ANTI_INJECTION_INSTRUCTION
)


async def job_agent(state: CareerPilotState) -> dict:
    """
    Analyze the job description and extract structured requirements.
    Raises transient exceptions for LangGraph RetryPolicy.
    """
    logger.info("[JobAgent] Starting job description analysis")

    job_description = state.get("job_description", "")
    if not job_description or len(job_description.strip()) < 50:
        logger.error("[JobAgent] Job description is empty or too short")
        return {
            "errors": [
                {
                    "step": WorkflowStep.JOB_AGENT,
                    "error": "Job description is empty or too short to analyze.",
                }
            ],
            "processing_log": ["JobAgent FAILED: empty job description"],
        }

    llm = get_structured_llm(JobAnalysis)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Please analyze the following job description and extract all structured information:\n\n"
                + wrap_user_content("JOB DESCRIPTION", job_description)
            )
        ),
    ]

    try:
        result: JobAnalysis = await llm.ainvoke(messages)
        logger.info(
            "[JobAgent] Done. Title: %s | Required skills: %d | Technologies: %d",
            result.job_title,
            len(result.required_skills),
            len(result.technologies),
        )
        return {
            "job_analysis": result,
            "completed_steps": [WorkflowStep.JOB_AGENT],
            "processing_log": [
                f"JobAgent completed. Role: {result.job_title} | Required skills: {len(result.required_skills)}"
            ],
        }

    except Exception as exc:
        if is_transient(exc):
            logger.warning("[JobAgent] Transient error (will retry): %s", exc)
            raise
        logger.exception("[JobAgent] Non-retryable error: %s", exc)
        return {
            "errors": [{"step": WorkflowStep.JOB_AGENT, "error": str(exc)}],
            "processing_log": [f"JobAgent FAILED: {exc}"],
        }

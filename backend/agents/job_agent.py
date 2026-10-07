"""
CareerPilot AI - Job Analysis Agent

Parses the job description and extracts structured requirements.
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import CareerPilotState
from llm import get_structured_llm
from schemas.models import JobAnalysis, WorkflowStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Senior Technical Recruiter and Job Description Analyst.

Your task is to carefully read a job description and extract structured information.

Guidelines:
- Separate required (must-have) skills from preferred (nice-to-have) skills.
- Identify ALL technologies mentioned, even incidentally.
- Determine the domain (e.g. ML Engineering, Backend, Data Science, Full Stack, DevOps).
- Estimate the seniority level from job title and requirements.
- If experience years are not explicitly stated, estimate from the responsibilities listed.
- Extract concrete responsibilities, not vague phrases.
"""


def job_agent(state: CareerPilotState) -> dict:
    """
    Analyze the job description and extract structured requirements.

    Args:
        state: Current workflow state containing job_description.

    Returns:
        Partial state update with job_analysis populated.
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
                    "retry_count": 0,
                }
            ],
            "processing_log": ["JobAgent FAILED: empty job description"],
            "next_step": WorkflowStep.END,
        }

    llm = get_structured_llm(JobAnalysis)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Please analyze the following job description:\n\n"
                f"---JOB DESCRIPTION START---\n{job_description}\n---JOB DESCRIPTION END---"
            )
        ),
    ]

    try:
        result: JobAnalysis = llm.invoke(messages)
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
                f"JobAgent completed. Role: {result.job_title} | "
                f"Required skills: {len(result.required_skills)}"
            ],
            "next_step": WorkflowStep.SKILL_AGENT,
        }

    except Exception as exc:
        logger.exception("[JobAgent] LLM call failed: %s", exc)
        return {
            "errors": [
                {
                    "step": WorkflowStep.JOB_AGENT,
                    "error": str(exc),
                    "retry_count": state.get("retry_counts", {}).get(
                        WorkflowStep.JOB_AGENT, 0
                    ),
                }
            ],
            "processing_log": [f"JobAgent FAILED: {exc}"],
            "next_step": WorkflowStep.END,
        }

"""
CareerPilot AI - Resume Agent

Extracts structured information from the candidate CV text.

Transient LLM errors are re-raised so LangGraph RetryPolicy can retry.
Non-retryable input validation errors return an error state immediately.
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.agent_runner import is_transient
from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.schemas.models import ResumeAnalysis, WorkflowStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert CV/Resume Analyst with years of experience in technical recruitment.\n\n"
    "Your task is to carefully read the provided resume text and extract structured information.\n\n"
    "Guidelines:\n"
    "- Be thorough and accurate - extract ALL skills, technologies, and experiences mentioned.\n"
    "- For AI/ML experience, specifically look for: Machine Learning, Deep Learning, NLP, LLMs,\n"
    "  LangChain, LangGraph, PyTorch, TensorFlow, scikit-learn, Hugging Face, OpenAI, etc.\n"
    "- Estimate total years of experience based on dates mentioned.\n"
    "- Extract both technical AND soft skills.\n"
    "- If information is not present, leave the field empty rather than guessing.\n"
    "- The candidate_name and contact_email may not always be present.\n"
    + ANTI_INJECTION_INSTRUCTION
)


async def resume_agent(state: CareerPilotState) -> dict:
    """
    Extract structured information from the candidate's resume.

    Raises transient exceptions so LangGraph RetryPolicy can retry.
    Returns error state for non-retryable input validation failures.
    """
    logger.info("[ResumeAgent] Starting resume analysis")

    resume_text = state.get("resume_text", "")
    if not resume_text or len(resume_text.strip()) < 50:
        logger.error("[ResumeAgent] Resume text is empty or too short")
        return {
            "errors": [{"step": WorkflowStep.RESUME_AGENT, "error": "Resume text is empty or too short to analyze."}],
            "processing_log": ["ResumeAgent FAILED: empty resume text"],
        }

    llm = get_structured_llm(ResumeAnalysis)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Please analyze the following resume and extract all structured information:\n\n"
                + wrap_user_content("RESUME", resume_text)
            )
        ),
    ]

    try:
        result: ResumeAnalysis = await llm.ainvoke(messages)
        logger.info(
            "[ResumeAgent] Done. Skills: %d | Experience entries: %d",

            len(result.technical_skills),
            len(result.experience),
        )
        return {
            "resume_analysis": result,
            "completed_steps": [WorkflowStep.RESUME_AGENT],
            "processing_log": [f"ResumeAgent completed. Found {len(result.technical_skills)} technical skills."],
        }

    except Exception as exc:
        if is_transient(exc):
            logger.warning("[ResumeAgent] Transient error (will retry): %s", exc)
            raise  # Let RetryPolicy handle it
        logger.exception("[ResumeAgent] Non-retryable error: %s", exc)
        return {
            "errors": [{"step": WorkflowStep.RESUME_AGENT, "error": str(exc)}],
            "processing_log": [f"ResumeAgent FAILED: {exc}"],
        }
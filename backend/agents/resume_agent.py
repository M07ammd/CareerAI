"""
CareerPilot AI - Resume Agent

Extracts structured information from the candidate's CV text.
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from graph.state import CareerPilotState
from llm import get_structured_llm
from schemas.models import ResumeAnalysis, WorkflowStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert CV/Resume Analyst with years of experience in technical recruitment.

Your task is to carefully read the provided resume text and extract structured information.

Guidelines:
- Be thorough and accurate - extract ALL skills, technologies, and experiences mentioned.
- For AI/ML experience, specifically look for: Machine Learning, Deep Learning, NLP, LLMs,
  LangChain, LangGraph, PyTorch, TensorFlow, scikit-learn, Hugging Face, OpenAI, etc.
- Estimate total years of experience based on dates mentioned.
- Extract both technical AND soft skills.
- If information is not present, leave the field empty rather than guessing.
- The candidate_name and contact_email may not always be present.
"""


def resume_agent(state: CareerPilotState) -> dict:
    """
    Extract structured information from the candidate's resume.

    Args:
        state: Current workflow state containing resume_text.

    Returns:
        Partial state update with resume_analysis populated.
    """
    logger.info("[ResumeAgent] Starting resume analysis")

    resume_text = state.get("resume_text", "")
    if not resume_text or len(resume_text.strip()) < 50:
        logger.error("[ResumeAgent] Resume text is empty or too short")
        return {
            "errors": [
                {
                    "step": WorkflowStep.RESUME_AGENT,
                    "error": "Resume text is empty or too short to analyze.",
                    "retry_count": 0,
                }
            ],
            "processing_log": ["ResumeAgent FAILED: empty resume text"],
            "next_step": WorkflowStep.END,
        }

    llm = get_structured_llm(ResumeAnalysis)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Please analyze the following resume and extract all structured information:\n\n"
                f"---RESUME START---\n{resume_text}\n---RESUME END---"
            )
        ),
    ]

    try:
        result: ResumeAnalysis = llm.invoke(messages)
        logger.info(
            "[ResumeAgent] Done. Candidate: %s | Skills: %d | Experience entries: %d",
            result.candidate_name,
            len(result.technical_skills),
            len(result.experience),
        )
        return {
            "resume_analysis": result,
            "completed_steps": [WorkflowStep.RESUME_AGENT],
            "processing_log": [
                f"ResumeAgent completed. Found {len(result.technical_skills)} technical skills."
            ],
            "next_step": WorkflowStep.JOB_AGENT,
        }

    except Exception as exc:
        logger.exception("[ResumeAgent] LLM call failed: %s", exc)
        return {
            "errors": [
                {
                    "step": WorkflowStep.RESUME_AGENT,
                    "error": str(exc),
                    "retry_count": state.get("retry_counts", {}).get(
                        WorkflowStep.RESUME_AGENT, 0
                    ),
                }
            ],
            "processing_log": [f"ResumeAgent FAILED: {exc}"],
            "next_step": WorkflowStep.END,
        }

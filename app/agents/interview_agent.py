"""
CareerPilot AI - Interview Agent

Generates personalised interview questions based on the candidate CV,
job description, and identified skill gaps.
Transient LLM errors propagate for RetryPolicy (optional agent).
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.agent_runner import is_transient
from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.schemas.models import InterviewQuestions, WorkflowStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a Senior Technical Interview Coach with expertise in preparing candidates for top-tier tech roles.\n\n"
    "Your task is to generate highly personalised interview questions for the candidate.\n\n"
    "Guidelines:\n"
    "- Technical questions MUST reference specific technologies from the job description.\n"
    "- Project questions MUST reference actual projects listed in the candidate CV.\n"
    "- Behavioral questions should probe for competencies relevant to the role.\n"
    "- HR questions should address potential concerns (gaps, career change, etc.).\n"
    "- Each question must include a rationale and 3-5 suggested answer points.\n"
    "- Questions should be challenging but fair at the level of the required seniority.\n"
    "- Generate at least 4 questions per category.\n\n"
    "The questions should NOT be generic. They should feel written specifically for THIS candidate applying to THIS job.\n"
    + ANTI_INJECTION_INSTRUCTION
)


async def interview_agent(state: CareerPilotState) -> dict:
    """
    Generate personalised interview questions.
    Optional agent: failure produces a warning, not an error status.
    Raises transient exceptions for LangGraph RetryPolicy.
    """
    logger.info("[InterviewAgent] Generating interview questions")

    resume_analysis = state.get("resume_analysis")
    job_analysis = state.get("job_analysis")
    skill_gaps = state.get("skill_gaps")
    skill_match = state.get("skill_match")

    if not resume_analysis or not job_analysis:
        return {
            "errors": [{"step": WorkflowStep.INTERVIEW_AGENT, "error": "Missing resume_analysis or job_analysis."}],
            "processing_log": ["InterviewAgent FAILED: missing prerequisite data"],
        }

    context_parts = [
        wrap_user_content("CANDIDATE PROFILE", json.dumps(resume_analysis.model_dump(), indent=2)),
        wrap_user_content("JOB REQUIREMENTS", json.dumps(job_analysis.model_dump(), indent=2)),
    ]
    if skill_match:
        context_parts.append(
            wrap_user_content(
                "SKILL MATCH",
                f"Score: {skill_match.match_score}\nMatched: {skill_match.matched_skills}\nMissing: {skill_match.missing_skills}",
            )
        )
    if skill_gaps:
        critical = skill_gaps.critical_blockers
        high = [g.skill for g in skill_gaps.high_priority_gaps]
        context_parts.append(wrap_user_content("SKILL GAPS", f"Critical: {critical}\nHigh Priority: {high}"))

    llm = get_structured_llm(InterviewQuestions)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="\n\n".join(context_parts)),
    ]

    try:
        result: InterviewQuestions = await llm.ainvoke(messages)
        total = (
            len(result.technical_questions) + len(result.project_questions)
            + len(result.behavioral_questions) + len(result.hr_questions)
        )
        logger.info(
            "[InterviewAgent] Done. Technical: %d | Project: %d | Behavioral: %d | HR: %d",
            len(result.technical_questions), len(result.project_questions),
            len(result.behavioral_questions), len(result.hr_questions),
        )
        return {
            "interview_questions": result,
            "completed_steps": [WorkflowStep.INTERVIEW_AGENT],
            "processing_log": [f"InterviewAgent completed. Generated {total} personalised questions."],
        }

    except Exception as exc:
        if is_transient(exc):
            logger.warning("[InterviewAgent] Transient error (will retry): %s", exc)
            raise
        logger.exception("[InterviewAgent] Non-retryable error: %s", exc)
        return {
            "errors": [{"step": WorkflowStep.INTERVIEW_AGENT, "error": str(exc)}],
            "processing_log": [f"InterviewAgent FAILED: {exc}"],
        }
"""
CareerPilot AI - Interview Service

Handles the logic for the mock interview turn endpoint.
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.llm import get_structured_llm
from app.schemas.models import InterviewTurnRequest, InterviewTurnResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""You are a Senior Technical Hiring Manager conducting an interview.
{ANTI_INJECTION_INSTRUCTION}

You will receive:
- The question that was asked.
- The candidate's answer.
- The candidate's resume context.
- The job description context.

Evaluate the answer based on:
1. Relevance to the question.
2. Technical accuracy and depth.
3. Alignment with the job requirements.
4. Use of the STAR method (if applicable).

Provide constructive feedback, a score out of 100, and optionally a follow-up question.
"""


async def handle_interview_turn(request: InterviewTurnRequest) -> InterviewTurnResponse:
    """Evaluate a candidate's answer to an interview question."""
    logger.info("Evaluating interview answer.")

    llm = get_structured_llm(InterviewTurnResponse)

    context = (
        wrap_user_content("JOB CONTEXT", request.job_context)
        + "\n\n"
        + wrap_user_content("RESUME CONTEXT", request.resume_context)
        + "\n\n"
        + wrap_user_content("QUESTION", request.question)
        + "\n\n"
        + wrap_user_content("ANSWER", request.answer)
    )

    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=context)]

    try:
        response = await llm.ainvoke(messages)
        return response
    except Exception as exc:
        logger.exception("Failed to evaluate interview answer: %s", exc)
        raise

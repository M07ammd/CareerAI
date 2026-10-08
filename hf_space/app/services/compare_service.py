"""
CareerPilot AI - Job Comparison Service

Compares a candidate's resume against multiple job descriptions to find the best fit.
"""

from __future__ import annotations

import asyncio
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.job_agent import job_agent
from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.llm import get_structured_llm
from app.schemas.models import CompareResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""You are a Senior Career Coach and Job Placement Expert.
{ANTI_INJECTION_INSTRUCTION}

You will receive:
- The candidate's resume text.
- A list of job descriptions.

Your task is to analyze how well the candidate fits each job, providing:
1. An overall match score (0-100) for each job.
2. The pros (strengths) of the candidate for that job.
3. The cons (gaps) of the candidate for that job.
4. A final recommendation on which job is the best fit overall and why.

Output the result adhering strictly to the required JSON schema.
"""


async def run_comparison(
    resume_text: str, job_descriptions: list[str]
) -> CompareResponse:
    """Compare a resume against multiple job descriptions."""
    logger.info("Comparing resume against %d job descriptions.", len(job_descriptions))

    llm = get_structured_llm(CompareResponse)

    tasks = [job_agent({"job_description": jd}) for jd in job_descriptions]
    job_results = await asyncio.gather(*tasks, return_exceptions=True)

    jds_context = ""
    for idx, (jd, res) in enumerate(zip(job_descriptions, job_results)):
        if isinstance(res, dict) and "job_analysis" in res:
            analysis_text = res["job_analysis"].model_dump_json(indent=2)
            jds_context += (
                wrap_user_content(f"JOB ANALYSIS {idx}", analysis_text) + "\n\n"
            )
        else:
            jds_context += wrap_user_content(f"JOB DESCRIPTION {idx}", jd) + "\n\n"

    context = wrap_user_content("CANDIDATE RESUME", resume_text) + "\n\n" + jds_context

    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=context)]

    try:
        response = await llm.ainvoke(messages)
        return response
    except Exception as exc:
        logger.exception("Failed to run comparison: %s", exc)
        raise

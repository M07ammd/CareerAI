"""
CareerPilot AI - Gap Analyzer Agent

Prioritizes missing skills and explains why each gap matters.
Optionally uses web search for current learning resources.
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings
from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.agents.prompt_utils import wrap_user_content, ANTI_INJECTION_INSTRUCTION
from app.schemas.models import SkillGaps, WorkflowStep
from app.tools.web_search import web_search

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Senior Career Coach and Skills Gap Analyst.

Your task is to analyse the missing skills from the candidate's profile and prioritize them.

Priority definitions:
- HIGH: Skills explicitly required by the job that the candidate lacks completely.
  Without these, the candidate will likely be rejected at screening.
- MEDIUM: Skills that are preferred or frequently appear in responsibilities.
  Having these improves the chance of success significantly.
- LOW: Nice-to-have skills or those where partial knowledge exists.

For each gap, provide:
1. Why it matters for this specific role.
2. Concrete learning resources or paths (courses, docs, projects).
3. A realistic time estimate to reach working proficiency.

Identify "critical blockers" — skills that would prevent the candidate from getting an interview.

Be practical and specific. Reference the actual job requirements and candidate background.
"""


async def gap_agent(state: CareerPilotState) -> dict:
    """
    Analyse and prioritise skill gaps, with optional web search enrichment.

    Args:
        state: Must contain skill_match and job_analysis.

    Returns:
        Partial state update with skill_gaps populated.
    """
    logger.info("[GapAgent] Starting gap analysis")

    skill_match = state.get("skill_match")
    job_analysis = state.get("job_analysis")
    resume_analysis = state.get("resume_analysis")

    if not skill_match or not job_analysis:
        return {
            "errors": [
                {
                    "step": WorkflowStep.GAP_AGENT,
                    "error": "Missing skill_match or job_analysis."}
            ],
            "processing_log": ["GapAgent FAILED: missing prerequisite data"]}

    # Optional web search for learning resources
    web_snippets: list[str] = []
    settings = get_settings()
    if settings.web_search_enabled and skill_match.missing_skills:
        top_missing = skill_match.missing_skills[:3]
        job_title = job_analysis.job_title
        for skill in top_missing:
            query = f"best way to learn {skill} for {job_title} 2024"
            results = web_search(query, max_results=2)
            web_snippets.extend(results)
            logger.debug("[GapAgent] Web search '%s' → %d results", query, len(results))

    context_parts = [
        f"=== SKILL MATCH RESULTS ===\n{json.dumps(skill_match.model_dump(), indent=2)}",
        f"=== JOB REQUIREMENTS ===\n{json.dumps(job_analysis.model_dump(), indent=2)}",
    ]
    if resume_analysis:
        context_parts.append(
            f"=== CANDIDATE BACKGROUND ===\n{json.dumps(resume_analysis.model_dump(), indent=2)}"
        )
    if web_snippets:
        context_parts.append(
            "=== WEB SEARCH RESULTS (for learning resources) ===\n"
            + "\n".join(f"• {s}" for s in web_snippets[:10])
        )

    llm = get_structured_llm(SkillGaps)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="\n\n".join(context_parts)),
    ]

    try:
        result: SkillGaps = await llm.ainvoke(messages)
        total_gaps = (
            len(result.high_priority_gaps)
            + len(result.medium_priority_gaps)
            + len(result.low_priority_gaps)
        )
        logger.info(
            "[GapAgent] Done. High: %d | Medium: %d | Low: %d",
            len(result.high_priority_gaps),
            len(result.medium_priority_gaps),
            len(result.low_priority_gaps),
        )
        return {
            "skill_gaps": result,
            "web_search_results": web_snippets,
            "completed_steps": [WorkflowStep.GAP_AGENT],
            "processing_log": [
                f"GapAgent completed. Total gaps: {total_gaps} "
                f"(High: {len(result.high_priority_gaps)}, "
                f"Medium: {len(result.medium_priority_gaps)}, "
                f"Low: {len(result.low_priority_gaps)})"
            ]}

    except Exception as exc:
        logger.exception("[GapAgent] LLM call failed: %s", exc)
        return {
            "errors": [
                {
                    "step": WorkflowStep.GAP_AGENT,
                    "error": str(exc)
                }
            ],
            "processing_log": [f"GapAgent FAILED: {exc}"]}

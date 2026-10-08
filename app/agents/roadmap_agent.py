"""
CareerPilot AI - Career Roadmap Agent

Creates a practical, actionable learning roadmap to bridge the skill gap.
Optional agent: transient errors propagate for RetryPolicy.
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.agent_runner import is_transient
from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.config import get_settings
from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.schemas.models import CareerRoadmap, WorkflowStep
from app.tools.web_search import async_web_search as web_search

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a Senior Career Strategist and Learning Path Designer.\n\n"
    "Your task is to create a practical, actionable career roadmap for the candidate.\n\n"
    "The roadmap has three horizons:\n"
    "1. Immediate actions (0-2 weeks): Quick wins, profile updates, application prep.\n"
    "2. Short-term goals (1-3 months): Skill building to address high-priority gaps.\n"
    "3. Long-term goals (3-12 months): Deep expertise, projects, career positioning.\n\n"
    "For each milestone:\n"
    "- Provide concrete, numbered action items.\n"
    "- List SPECIFIC learning resources (real course names, documentation, GitHub repos).\n"
    "- Set measurable success metrics.\n"
    "- Be realistic about time estimates.\n\n"
    "Incorporate the web search results to suggest current, relevant resources.\n"
    "Be specific — not generic. Reference the actual gaps and the actual role.\n"
    + ANTI_INJECTION_INSTRUCTION
)


async def roadmap_agent(state: CareerPilotState) -> dict:
    """
    Generate a personalised career roadmap.
    Optional agent: transient errors propagate for LangGraph RetryPolicy.
    """
    logger.info("[RoadmapAgent] Building career roadmap")

    skill_gaps = state.get("skill_gaps")
    job_analysis = state.get("job_analysis")
    resume_analysis = state.get("resume_analysis")
    skill_match = state.get("skill_match")

    if not skill_gaps or not job_analysis:
        return {
            "errors": [
                {
                    "step": WorkflowStep.ROADMAP_AGENT,
                    "error": "Missing skill_gaps or job_analysis.",
                }
            ],
            "processing_log": ["RoadmapAgent FAILED: missing prerequisite data"],
        }

    # Targeted web searches for learning paths
    web_snippets: list[str] = []
    settings = get_settings()
    if settings.web_search_enabled:
        from datetime import datetime

        year = datetime.now().year
        queries = [
            f"best {job_analysis.job_title} learning roadmap {year}",
            f"top certifications for {job_analysis.domain} engineers {year}",
        ]
        if skill_gaps.high_priority_gaps:
            top_skill = skill_gaps.high_priority_gaps[0].skill
            queries.append(f"best online course for {top_skill} {year}")

        for q in queries:
            try:
                results = await web_search(q, max_results=3)
                web_snippets.extend(results)
            except Exception as search_exc:
                logger.warning(
                    "[RoadmapAgent] Web search failed (non-fatal): %s", search_exc
                )

    context_parts = [
        wrap_user_content(
            "ROLE TARGET",
            f"Title: {job_analysis.job_title}\nDomain: {job_analysis.domain}",
        ),
        wrap_user_content("SKILL GAPS", json.dumps(skill_gaps.model_dump(), indent=2)),
    ]
    if skill_match:
        context_parts.append(
            wrap_user_content(
                "CURRENT MATCH SCORE",
                f"{skill_match.match_score}/100\nStrengths: {skill_match.strengths}",
            )
        )
    if resume_analysis:
        context_parts.append(
            wrap_user_content(
                "CANDIDATE BACKGROUND",
                f"Experience: {resume_analysis.total_experience_years} years\nCurrent skills: {resume_analysis.technical_skills[:20]}",
            )
        )
    if web_snippets:
        context_parts.append(
            wrap_user_content(
                "WEB SEARCH RESULTS", "\n".join(f"- {s}" for s in web_snippets[:12])
            )
        )

    llm = get_structured_llm(CareerRoadmap)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="\n\n".join(context_parts)),
    ]

    try:
        result: CareerRoadmap = await llm.ainvoke(messages)
        total_milestones = (
            len(result.immediate_actions)
            + len(result.short_term_goals)
            + len(result.long_term_goals)
        )
        logger.info(
            "[RoadmapAgent] Done. Milestones: %d | Projects: %d | Certs: %d",
            total_milestones,
            len(result.recommended_projects),
            len(result.recommended_certifications),
        )
        return {
            "career_roadmap": result,
            "web_search_results": web_snippets,
            "completed_steps": [WorkflowStep.ROADMAP_AGENT],
            "processing_log": [
                f"RoadmapAgent completed. Created {total_milestones} milestones."
            ],
        }

    except Exception as exc:
        if is_transient(exc):
            logger.warning("[RoadmapAgent] Transient error (will retry): %s", exc)
            raise
        logger.exception("[RoadmapAgent] Non-retryable error: %s", exc)
        return {
            "errors": [{"step": WorkflowStep.ROADMAP_AGENT, "error": str(exc)}],
            "processing_log": [f"RoadmapAgent FAILED: {exc}"],
        }

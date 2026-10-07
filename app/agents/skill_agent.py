"""
CareerPilot AI - Skill Matching Agent

Compares the candidate's skills against the job requirements and produces
a detailed match report with a 0–100 match score.
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.agents.prompt_utils import wrap_user_content, ANTI_INJECTION_INSTRUCTION
from app.schemas.models import SkillMatch, WorkflowStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Technical Skills Matching Expert.

Your task is to compare a candidate's skills and experience with the requirements in a job description.

Guidelines:
- Compare each required and preferred skill from the job against the candidate's profile.
- A "matched" skill is one the candidate clearly has (even under a different name/version).
- A "partially matched" skill is one the candidate has some exposure to but not full mastery.
- A "missing" skill is one absent from the candidate's profile entirely.
- The match_score (0–100) should reflect: how many required skills are met, depth of experience,
  and overall fit for the role.
- Be specific in your explanations — reference actual skills and experience from the CV.
- Provide an `evidence_grounded_justification` with direct quotes or facts from the CV supporting the score.
- Do NOT inflate the score. Be honest and calibrated.
"""


async def skill_agent(state: CareerPilotState) -> dict:
    """
    Match candidate skills against job requirements.

    Args:
        state: Must contain resume_analysis and job_analysis.

    Returns:
        Partial state update with skill_match populated.
    """
    logger.info("[SkillAgent] Starting skill matching")

    resume_analysis = state.get("resume_analysis")
    job_analysis = state.get("job_analysis")

    if not resume_analysis or not job_analysis:
        logger.error("[SkillAgent] Missing prerequisite data")
        return {
            "errors": [
                {
                    "step": WorkflowStep.SKILL_AGENT,
                    "error": "Missing resume_analysis or job_analysis."}
            ],
            "processing_log": ["SkillAgent FAILED: missing prerequisite data"]}

    resume_summary = json.dumps(resume_analysis.model_dump(), indent=2)
    job_summary = json.dumps(job_analysis.model_dump(), indent=2)

    llm = get_structured_llm(SkillMatch)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Please compare the following candidate profile with the job requirements.\n\n"
                f"=== CANDIDATE PROFILE ===\n{resume_summary}\n\n"
                f"=== JOB REQUIREMENTS ===\n{job_summary}"
            )
        ),
    ]

    try:
        result: SkillMatch = await llm.ainvoke(messages)
        
        # Deterministic scoring
        total_skills = len(result.matched_skills) + len(result.missing_skills) + len(result.partially_matched_skills)
        if total_skills == 0:
            result.match_score = 0
        else:
            base_score = (len(result.matched_skills) * 1.0 + len(result.partially_matched_skills) * 0.5) / total_skills
            result.match_score = int(base_score * 100)
            
        logger.info(
            "[SkillAgent] Done. Score: %d | Matched: %d | Missing: %d",
            result.match_score,
            len(result.matched_skills),
            len(result.missing_skills),
        )
        return {
            "skill_match": result,
            "completed_steps": [WorkflowStep.SKILL_AGENT],
            "processing_log": [
                f"SkillAgent completed. Match score: {result.match_score:.1f}/100. "
                f"Matched: {len(result.matched_skills)}, Missing: {len(result.missing_skills)}"
            ]}

    except Exception as exc:
        logger.exception("[SkillAgent] LLM call failed: %s", exc)
        return {
            "errors": [
                {
                    "step": WorkflowStep.SKILL_AGENT,
                    "error": str(exc)
                }
            ],
            "processing_log": [f"SkillAgent FAILED: {exc}"]}

"""
CareerPilot AI - Skill Matching Agent

Compares the candidate skills against job requirements and produces a
deterministic 0-100 match score.

Score formula (documented):
  required_skills  weight = 70
  preferred_skills weight = 30
  partial match    = 0.5 of full weight

Transient LLM errors propagate for RetryPolicy; missing prereqs returned immediately.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.agent_runner import is_transient
from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.schemas.models import SkillMatch, WorkflowStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a Technical Skills Matching Expert.\n\n"
    "Your task is to compare a candidate's skills and experience with the requirements in a job description.\n\n"
    "Guidelines:\n"
    "- Compare each required and preferred skill from the job against the candidate's profile.\n"
    "- A 'matched' skill is one the candidate clearly has (even under a different name/version).\n"
    "- A 'partially matched' skill is one the candidate has some exposure to but not full mastery.\n"
    "- A 'missing' skill is one absent from the candidate's profile entirely.\n"
    "- Be specific in your explanations - reference actual skills and experience from the CV.\n"
    "- Provide an evidence_grounded_justification with direct quotes or facts from the CV supporting the score.\n"
    "- Do NOT inflate the score. Be honest and calibrated.\n"
    + ANTI_INJECTION_INSTRUCTION
)

# Score weights
_REQUIRED_WEIGHT = 70
_PREFERRED_WEIGHT = 30
_PARTIAL_FACTOR = 0.5


def compute_deterministic_score(
    required: Sequence[str],
    preferred: Sequence[str],
    matched: Sequence[str],
    partial: Sequence[str],
) -> int:
    """
    Compute a 0-100 match score from skill lists.

    Weights: required skills account for 70 points, preferred for 30.
    Partial matches count as half. Skills the LLM adds that are not in the
    JD lists are ignored. JD skills the LLM omits are counted as missing.

    Returns an integer 0-100.
    """
    matched_set = {s.lower().strip() for s in matched}

    partial_set = set()
    for p in partial:
        if isinstance(p, str):
            partial_set.add(p.lower().strip())
        else:
            partial_set.add(p.skill.lower().strip())

    req_total = len(required)
    pref_total = len(preferred)

    def _score_list(skills: Sequence[str], weight: float) -> float:
        if not skills:
            return weight  # no skills required → full points for that bucket
        points = 0.0
        for skill in skills:
            key = skill.lower().strip()
            if key in matched_set:
                points += 1.0
            elif key in partial_set:
                points += _PARTIAL_FACTOR
        return weight * (points / len(skills))

    req_score = _score_list(required, _REQUIRED_WEIGHT)
    pref_score = _score_list(preferred, _PREFERRED_WEIGHT)
    return round(req_score + pref_score)


async def skill_agent(state: CareerPilotState) -> dict:
    """
    Match candidate skills against job requirements.
    Score is computed deterministically in code from the LLM's skill judgements.
    Raises transient exceptions for LangGraph RetryPolicy.
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
                    "error": "Missing resume_analysis or job_analysis.",
                }
            ],
            "processing_log": ["SkillAgent FAILED: missing prerequisite data"],
        }

    resume_summary = json.dumps(resume_analysis.model_dump(), indent=2)
    job_summary = json.dumps(job_analysis.model_dump(), indent=2)

    llm = get_structured_llm(SkillMatch)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Please compare the following candidate profile with the job requirements.\n\n"
                + wrap_user_content("CANDIDATE PROFILE", resume_summary)
                + "\n\n"
                + wrap_user_content("JOB REQUIREMENTS", job_summary)
            )
        ),
    ]

    try:
        result: SkillMatch = await llm.ainvoke(messages)

        # Deterministic score overrides any LLM-assigned score
        required = job_analysis.required_skills or []
        preferred = job_analysis.preferred_skills or []
        result.match_score = compute_deterministic_score(
            required, preferred, result.matched_skills, result.partially_matched_skills
        )

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
                f"SkillAgent completed. Match score: {result.match_score}/100. "
                f"Matched: {len(result.matched_skills)}, Missing: {len(result.missing_skills)}"
            ],
        }

    except Exception as exc:
        if is_transient(exc):
            logger.warning("[SkillAgent] Transient error (will retry): %s", exc)
            raise
        logger.exception("[SkillAgent] Non-retryable error: %s", exc)
        return {
            "errors": [{"step": WorkflowStep.SKILL_AGENT, "error": str(exc)}],
            "processing_log": [f"SkillAgent FAILED: {exc}"],
        }

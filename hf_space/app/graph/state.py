"""
CareerPilot AI - LangGraph State

Defines the shared TypedDict state passed between all agents.
"""

from __future__ import annotations

import operator
from typing import Annotated

from typing_extensions import TypedDict

from app.schemas.models import (
    CareerRoadmap,
    FinalReport,
    InterviewQuestions,
    JobAnalysis,
    ResumeAnalysis,
    SkillGaps,
    SkillMatch,
)


class AgentError(TypedDict):
    step: str
    error: str


class CareerPilotState(TypedDict):
    # ---- User inputs -------------------------------------------------------
    resume_text: str  # Raw text extracted from CV PDF
    job_description: str  # Raw job description text

    # ---- Agent outputs -----------------------------------------------------
    resume_analysis: ResumeAnalysis | None
    job_analysis: JobAnalysis | None
    skill_match: SkillMatch | None
    skill_gaps: SkillGaps | None
    interview_questions: InterviewQuestions | None
    career_roadmap: CareerRoadmap | None
    final_report: FinalReport | None

    # ---- Workflow control --------------------------------------------------
    completed_steps: Annotated[list[str], operator.add]  # Accumulate completed steps

    # ---- Error tracking ----------------------------------------------------
    errors: Annotated[list[AgentError], operator.add]

    # ---- Metadata ----------------------------------------------------------
    web_search_results: Annotated[
        list[str], operator.add
    ]  # Accumulated search snippets
    processing_log: Annotated[list[str], operator.add]  # Human-readable log


def get_initial_state(resume_text: str, job_description: str) -> CareerPilotState:
    """Return the initial state for a new analysis run."""
    return CareerPilotState(
        resume_text=resume_text,
        job_description=job_description,
        resume_analysis=None,
        job_analysis=None,
        skill_match=None,
        skill_gaps=None,
        interview_questions=None,
        career_roadmap=None,
        final_report=None,
        completed_steps=[],
        errors=[],
        web_search_results=[],
        processing_log=["Workflow started"],
    )

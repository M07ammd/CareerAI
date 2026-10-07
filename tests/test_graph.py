"""
Tests for the LangGraph routing logic.
"""

import pytest

from app.graph.router import supervisor_router
from app.graph.state import CareerPilotState, get_initial_state
from app.schemas.models import WorkflowStep


def make_state(**overrides) -> CareerPilotState:
    base = get_initial_state(
        resume_text="Software engineer with Python skills.",
        job_description="We are hiring a Python developer with 3+ years of experience.",
    )
    base.update(overrides)
    return base


class TestSupervisorRouter:
    def test_routes_to_resume_agent(self):
        state = make_state(errors=[], retry_counts={})
        result = supervisor_router(state)
        assert result == "resume_agent"

    def test_routes_to_job_agent(self):
        state = make_state(resume_analysis={"dummy": "data"}, errors=[], retry_counts={})
        assert supervisor_router(state) == "job_agent"

    def test_routes_to_skill_agent(self):
        state = make_state(resume_analysis={}, job_analysis={}, errors=[], retry_counts={})
        assert supervisor_router(state) == "skill_agent"

    def test_routes_to_end_on_end_step(self):
        state = make_state(
            resume_analysis={}, job_analysis={}, skill_match={}, skill_gaps={},
            interview_questions={}, career_roadmap={}, final_report={},
            errors=[], retry_counts={}
        )
        assert supervisor_router(state) == "__end__"

    def test_aborts_after_max_retries(self):
        """After MAX_RETRIES failures, supervisor should route to END."""
        state = make_state(
            errors=[
                {
                    "step": WorkflowStep.RESUME_AGENT,
                    "error": "LLM timeout",
                    "retry_count": 2,
                }
            ],
            retry_counts={WorkflowStep.RESUME_AGENT: 2},
        )
        result = supervisor_router(state)
        assert result == "__end__"

    def test_allows_retry_before_max(self):
        """With fewer than MAX_RETRIES failures, supervisor allows retry."""
        state = make_state(
            errors=[
                {
                    "step": WorkflowStep.RESUME_AGENT,
                    "error": "LLM timeout",
                    "retry_count": 1,
                }
            ],
            retry_counts={WorkflowStep.RESUME_AGENT: 1},
        )
        result = supervisor_router(state)
        assert result == "resume_agent"

    def test_routes_to_report_agent(self):
        state = make_state(
            resume_analysis={}, job_analysis={}, skill_match={}, skill_gaps={},
            interview_questions={}, career_roadmap={},
            errors=[], retry_counts={}
        )
        assert supervisor_router(state) == "report_agent"


class TestGetInitialState:
    def test_initial_state_structure(self):
        state = get_initial_state("My CV text", "Job description text")
        assert state["resume_text"] == "My CV text"
        assert state["job_description"] == "Job description text"
        assert state["resume_analysis"] is None
        assert state["completed_steps"] == []
        assert state["errors"] == []
        assert state["next_step"] == WorkflowStep.RESUME_AGENT

    def test_initial_state_defaults(self):
        state = get_initial_state("CV", "JD")
        assert state["retry_counts"] == {}
        assert state["web_search_results"] == []
        assert len(state["processing_log"]) >= 1

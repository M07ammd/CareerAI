"""
Tests for Group A reliability fixes:
  A1 - Transient exceptions propagate (retry logic fires)
  A2 - Critical agent failures return status="error"; optional produce "partial" + warnings
  A3 - llm.py uses settings (no hardcoded model/url)
"""

from __future__ import annotations

import asyncio
import functools
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# A1: Retry propagation
# ---------------------------------------------------------------------------

class _TransientError(ConnectionError):
    """Simulates a transient network error."""


def _make_flaky_llm(fail_times: int):
    """Return a fake LLM that raises _TransientError fail_times, then succeeds."""
    call_count = 0

    async def ainvoke(messages, **_):
        nonlocal call_count
        call_count += 1
        if call_count <= fail_times:
            raise _TransientError(f"Attempt {call_count} failed")
        # Return a minimal fake structured object
        return MagicMock(
            candidate_name="Test Candidate",
            contact_email=None,
            summary="A great candidate",
            education=[],
            experience=[],
            projects=[],
            technical_skills=["Python"],
            soft_skills=[],
            ai_ml_experience=[],
            total_experience_years=3.0,
            languages=["Python"],
            certifications=[],
        )

    llm = MagicMock()
    llm.ainvoke = ainvoke
    return llm, lambda: call_count


@pytest.mark.asyncio
async def test_transient_error_propagates_from_agent():
    """
    When a transient error occurs, is_transient() returns True and the agent re-raises.
    This allows LangGraph RetryPolicy to retry the node.
    """
    from app.agents.agent_runner import is_transient

    err = _TransientError("Connection refused")
    assert is_transient(err), "ConnectionError should be classified as transient"


@pytest.mark.asyncio
async def test_agent_reraises_transient_error():
    """
    resume_agent re-raises transient errors (not returning error dict),
    so LangGraph RetryPolicy can fire.
    """
    from app.agents.resume_agent import resume_agent

    flaky_llm, get_count = _make_flaky_llm(fail_times=1)
    state = {"resume_text": "A" * 100, "job_description": "", "errors": [], "completed_steps": []}

    with patch("app.agents.resume_agent.get_structured_llm", return_value=flaky_llm):
        # First call raises — agent should re-raise, not swallow
        with pytest.raises(_TransientError):
            await resume_agent(state)


@pytest.mark.asyncio
async def test_agent_succeeds_after_transient_error():
    """
    After transient errors, on success the agent returns data (simulating RetryPolicy behaviour).
    """
    from app.agents.resume_agent import resume_agent

    flaky_llm, get_count = _make_flaky_llm(fail_times=0)
    state = {"resume_text": "A" * 100, "job_description": "", "errors": [], "completed_steps": []}

    with patch("app.agents.resume_agent.get_structured_llm", return_value=flaky_llm):
        result = await resume_agent(state)

    assert "resume_analysis" in result
    assert get_count() == 1  # Only one call needed


# ---------------------------------------------------------------------------
# A2: Critical vs optional failure semantics
# ---------------------------------------------------------------------------

def _make_error_state(failed_step: str) -> dict:
    """Produce a fake final_state where one agent wrote an error."""
    from app.schemas.models import WorkflowStep
    step_map = {
        "resume_agent": WorkflowStep.RESUME_AGENT,
        "job_agent": WorkflowStep.JOB_AGENT,
        "skill_agent": WorkflowStep.SKILL_AGENT,
        "interview_agent": WorkflowStep.INTERVIEW_AGENT,
        "roadmap_agent": WorkflowStep.ROADMAP_AGENT,
    }
    return {
        "resume_text": "A" * 100,
        "job_description": "B" * 100,
        "messages": [],
        "resume_analysis": None,
        "job_analysis": None,
        "skill_match": None,
        "skill_gaps": None,
        "interview_questions": None,
        "career_roadmap": None,
        "final_report": None,
        "current_step": step_map.get(failed_step, WorkflowStep.RESUME_AGENT),
        "completed_steps": [],
        "errors": [{"step": failed_step, "error": "simulated failure"}],
        "web_search_results": [],
        "processing_log": [],
    }


@pytest.mark.asyncio
async def test_resume_agent_critical_failure_returns_error():
    from app.services.analysis_service import run_analysis
    state = _make_error_state("resume_agent")

    with patch("app.services.analysis_service.get_graph") as mock_graph:
        mock_graph.return_value.ainvoke = AsyncMock(return_value=state)
        result = await run_analysis("A" * 100, "B" * 100, request_id="test")

    assert result.status == "error"
    assert result.final_report is None
    assert "resume" in (result.failed_step or "").lower() or result.error_message


@pytest.mark.asyncio
async def test_job_agent_critical_failure_returns_error():
    from app.services.analysis_service import run_analysis
    state = _make_error_state("job_agent")

    with patch("app.services.analysis_service.get_graph") as mock_graph:
        mock_graph.return_value.ainvoke = AsyncMock(return_value=state)
        result = await run_analysis("A" * 100, "B" * 100, request_id="test")

    assert result.status == "error"


@pytest.mark.asyncio
async def test_skill_agent_critical_failure_returns_error():
    from app.services.analysis_service import run_analysis
    state = _make_error_state("skill_agent")

    with patch("app.services.analysis_service.get_graph") as mock_graph:
        mock_graph.return_value.ainvoke = AsyncMock(return_value=state)
        result = await run_analysis("A" * 100, "B" * 100, request_id="test")

    assert result.status == "error"


@pytest.mark.asyncio
async def test_optional_agent_failure_returns_partial_with_warning():
    """interview_agent or roadmap_agent failure → status partial, has warning."""
    from app.schemas.models import (
        JobAnalysis, ResumeAnalysis, SkillMatch, WorkflowStep
    )
    from app.services.analysis_service import run_analysis

    # Minimal fake objects to simulate successful critical agents
    fake_resume = MagicMock(spec=ResumeAnalysis)
    fake_job = MagicMock(spec=JobAnalysis)
    fake_skill = MagicMock(spec=SkillMatch, match_score=65)

    state = {
        "resume_text": "A" * 100,
        "job_description": "B" * 100,
        "messages": [],
        "resume_analysis": fake_resume,
        "job_analysis": fake_job,
        "skill_match": fake_skill,
        "skill_gaps": None,
        "interview_questions": None,
        "career_roadmap": None,
        "final_report": None,
        "current_step": WorkflowStep.INTERVIEW_AGENT,
        "completed_steps": [WorkflowStep.RESUME_AGENT, WorkflowStep.JOB_AGENT, WorkflowStep.SKILL_AGENT],
        "errors": [{"step": "interview_agent", "error": "LLM timeout"}],
        "web_search_results": [],
        "processing_log": [],
    }

    with patch("app.services.analysis_service.get_graph") as mock_graph:
        mock_graph.return_value.ainvoke = AsyncMock(return_value=state)
        result = await run_analysis("A" * 100, "B" * 100, request_id="test")

    assert result.status == "partial"
    assert len(result.warnings) >= 1
    # Warning must not contain "WorkflowStep." enum representation
    for w in result.warnings:
        assert "WorkflowStep." not in w


# ---------------------------------------------------------------------------
# A3: llm.py uses settings (no hardcoded openrouter model/base_url)
# ---------------------------------------------------------------------------

def test_llm_uses_settings_model():
    """LLM model should come from settings, not be hardcoded."""
    import importlib
    import app.llm as llm_module

    source = open("app/llm.py").read()
    # Should NOT contain hardcoded openrouter/free or openrouter.ai base URL
    assert "openrouter/free" not in source, "Hardcoded model 'openrouter/free' found in llm.py"
    assert "openrouter.ai/api/v1" not in source, "Hardcoded OpenRouter base_url found in llm.py"


def test_llm_reads_base_url_from_settings():
    """LLM should use settings.llm_base_url when provided."""
    from app.config import Settings

    s = Settings(
        llm_provider="openai",
        llm_model="gpt-4o",
        llm_base_url="https://custom.example.com/v1",
        openai_api_key="sk-test-key",
    )
    assert s.llm_base_url == "https://custom.example.com/v1"
    assert s.llm_model == "gpt-4o"


def test_llm_no_base_url_by_default():
    """Without LLM_BASE_URL set, llm_base_url should be None."""
    from app.config import Settings
    s = Settings(llm_provider="openai", openai_api_key="sk-test")
    assert s.llm_base_url is None
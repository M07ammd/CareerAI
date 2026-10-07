"""
Tests for individual agent logic (unit-level, with mocked LLMs).
"""

import json
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from app.graph.state import get_initial_state
from app.schemas.models import (
    JobAnalysis,
    ResumeAnalysis,
    SkillGaps,
    SkillMatch,
    WorkflowStep,
)


def make_resume_state(**overrides):
    s = get_initial_state(
        resume_text=(
            "Alice Smith | alice@example.com\n"
            "ML Engineer | Python, PyTorch, scikit-learn, LangChain\n"
            "Experience: 4 years at Acme Corp building recommendation systems.\n"
            "Education: M.Sc. Computer Science, Stanford 2020\n"
            "Projects: Built a sentiment analysis pipeline using BERT."
        ),
        job_description=(
            "Senior ML Engineer required. Must have: Python, PyTorch, LangChain, LangGraph. "
            "Nice to have: Kubernetes, Terraform. 5+ years experience preferred."
        ),
    )
    s.update(overrides)
    return s


class TestResumeAgent:
    @patch("app.agents.resume_agent.get_structured_llm")
    @pytest.mark.asyncio
    async def test_successful_extraction(self, mock_get_llm):
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = ResumeAnalysis(
            candidate_name="Alice Smith",
            summary="ML Engineer with 4 years experience",
            technical_skills=["Python", "PyTorch", "scikit-learn"],
            ai_ml_experience=["BERT", "LangChain"],
        )
        mock_get_llm.return_value = mock_llm

        from app.agents.resume_agent import resume_agent

        state = make_resume_state()
        result = await resume_agent(state)

        assert "resume_analysis" in result
        assert result["resume_analysis"].candidate_name == "Alice Smith"
        assert WorkflowStep.RESUME_AGENT in result["completed_steps"]

    @patch("app.agents.resume_agent.get_structured_llm")
    @pytest.mark.asyncio
    async def test_llm_failure_returns_error(self, mock_get_llm):
        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception("LLM timeout")
        mock_get_llm.return_value = mock_llm

        from app.agents.resume_agent import resume_agent

        state = make_resume_state()
        result = await resume_agent(state)

        assert "errors" in result
        assert len(result["errors"]) == 1

    @pytest.mark.asyncio
    async def test_empty_resume_text_returns_error(self):
        from app.agents.resume_agent import resume_agent

        state = get_initial_state(resume_text="", job_description="Valid JD here")
        result = await resume_agent(state)

        assert "errors" in result


class TestJobAgent:
    @patch("app.agents.job_agent.get_structured_llm")
    @pytest.mark.asyncio
    async def test_successful_extraction(self, mock_get_llm):
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = JobAnalysis(
            job_title="Senior ML Engineer",
            required_skills=["Python", "PyTorch"],
            domain="ML Engineering",
            seniority_level="Senior",
        )
        mock_get_llm.return_value = mock_llm

        from app.agents.job_agent import job_agent

        state = make_resume_state()
        result = await job_agent(state)

        assert "job_analysis" in result
        assert result["job_analysis"].job_title == "Senior ML Engineer"

    @pytest.mark.asyncio
    async def test_empty_jd_returns_error(self):
        from app.agents.job_agent import job_agent

        state = get_initial_state(resume_text="Valid resume", job_description="")
        result = await job_agent(state)

        assert "errors" in result


class TestSkillAgent:
    @patch("app.agents.skill_agent.get_structured_llm")
    @pytest.mark.asyncio
    async def test_successful_matching(self, mock_get_llm):
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = SkillMatch(
            matched_skills=["Python", "PyTorch"],
            missing_skills=["LangGraph"],
            match_score=72.0,
            explanation="Good match overall.",
        )
        mock_get_llm.return_value = mock_llm

        from app.agents.skill_agent import skill_agent

        state = make_resume_state(
            resume_analysis=ResumeAnalysis(
                summary="ML Engineer",
                technical_skills=["Python", "PyTorch"],
            ),
            job_analysis=JobAnalysis(
                job_title="ML Engineer",
                required_skills=["Python", "PyTorch", "LangGraph"],
                domain="ML Engineering",
                seniority_level="Senior",
            ),
        )
        result = await skill_agent(state)

        assert "skill_match" in result
        assert result["skill_match"].match_score == 66

    @pytest.mark.asyncio
    async def test_missing_prerequisites_returns_error(self):
        from app.agents.skill_agent import skill_agent

        state = make_resume_state()  # no resume_analysis or job_analysis set
        result = await skill_agent(state)

        assert "errors" in result

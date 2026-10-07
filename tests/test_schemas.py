"""
Tests for Pydantic schema models.
"""

import pytest
from pydantic import ValidationError

from app.schemas.models import (
    AnalysisResponse,
    CareerRoadmap,
    EducationEntry,
    ExperienceEntry,
    FinalReport,
    InterviewQuestion,
    InterviewQuestions,
    JobAnalysis,
    MatchLevel,
    ProjectEntry,
    ResumeAnalysis,
    RoadmapMilestone,
    SkillGapItem,
    SkillGaps,
    SkillMatch,
    SkillMatchDetail,
    SkillPriority,
    WorkflowStep,
)


class TestResumeAnalysis:
    def test_minimal_valid(self):
        ra = ResumeAnalysis(summary="A competent developer.")
        assert ra.summary == "A competent developer."
        assert ra.technical_skills == []
        assert ra.ai_ml_experience == []

    def test_full_valid(self):
        ra = ResumeAnalysis(
            candidate_name="Alice Smith",
            contact_email="alice@example.com",
            summary="Senior ML engineer with 5 years of experience.",
            education=[
                EducationEntry(
                    degree="B.Sc. Computer Science",
                    institution="MIT",
                    year="2018",
                )
            ],
            experience=[
                ExperienceEntry(
                    title="ML Engineer",
                    company="OpenAI",
                    duration="2020–2023",
                    responsibilities=["Built LLM pipelines"],
                    technologies=["Python", "PyTorch"],
                )
            ],
            technical_skills=["Python", "PyTorch", "LangChain"],
            ai_ml_experience=["GPT-4", "BERT", "LangGraph"],
            total_experience_years=5.0,
        )
        assert ra.candidate_name == "Alice Smith"
        assert len(ra.experience) == 1
        assert ra.total_experience_years == 5.0

    def test_optional_fields_default_none(self):
        ra = ResumeAnalysis(summary="Test candidate.")
        assert ra.candidate_name is None
        assert ra.contact_email is None
        assert ra.total_experience_years is None


class TestJobAnalysis:
    def test_valid(self):
        ja = JobAnalysis(
            job_title="Senior ML Engineer",
            required_skills=["Python", "PyTorch"],
            domain="ML Engineering",
            seniority_level="Senior",
        )
        assert ja.job_title == "Senior ML Engineer"
        assert "Python" in ja.required_skills

    def test_missing_required_fields_raises(self):
        with pytest.raises(ValidationError):
            JobAnalysis()  # job_title, domain, seniority_level are required


class TestSkillMatch:
    def test_valid_score_range(self):
        sm = SkillMatch(
            match_score=75,
            explanation="Good match overall.",
        )
        assert sm.match_score == 75

    def test_score_below_zero_raises(self):
        with pytest.raises(ValidationError):
            SkillMatch(match_score=-1.0, explanation="Test")

    def test_score_above_100_raises(self):
        with pytest.raises(ValidationError):
            SkillMatch(match_score=101.0, explanation="Test")

    def test_partial_skills(self):
        sm = SkillMatch(
            match_score=60.0,
            explanation="Partial match.",
            partially_matched_skills=[
                SkillMatchDetail(
                    skill="Kubernetes",
                    level=MatchLevel.PARTIAL,
                    notes="Has Docker experience",
                )
            ],
        )
        assert len(sm.partially_matched_skills) == 1
        assert sm.partially_matched_skills[0].level == MatchLevel.PARTIAL


class TestSkillGaps:
    def test_priorities(self):
        sg = SkillGaps(
            overall_gap_summary="Several critical gaps.",
            high_priority_gaps=[
                SkillGapItem(
                    skill="Kubernetes",
                    priority=SkillPriority.HIGH,
                    reason="Required for deployment",
                )
            ],
            medium_priority_gaps=[
                SkillGapItem(
                    skill="Terraform",
                    priority=SkillPriority.MEDIUM,
                    reason="Preferred for infrastructure",
                )
            ],
        )
        assert len(sg.high_priority_gaps) == 1
        assert sg.high_priority_gaps[0].priority == SkillPriority.HIGH
        assert len(sg.medium_priority_gaps) == 1


class TestInterviewQuestions:
    def test_valid(self):
        iq = InterviewQuestions(
            technical_questions=[
                InterviewQuestion(
                    question="Explain transformers.",
                    category="Technical",
                    rationale="Core ML concept for the role.",
                )
            ],
            preparation_tips=["Research the company"],
        )
        assert len(iq.technical_questions) == 1

    def test_empty_is_valid(self):
        iq = InterviewQuestions()
        assert iq.technical_questions == []


class TestCareerRoadmap:
    def test_valid(self):
        cr = CareerRoadmap(
            career_trajectory="Path to Staff ML Engineer",
            immediate_actions=[
                RoadmapMilestone(
                    title="Update LinkedIn",
                    description="Refresh profile with recent projects",
                    timeframe="Week 1",
                )
            ],
        )
        assert len(cr.immediate_actions) == 1
        assert cr.career_trajectory == "Path to Staff ML Engineer"


class TestFinalReport:
    def test_valid(self):
        fr = FinalReport(
            job_title="ML Engineer",
            executive_summary="Candidate shows strong potential.",
            match_score=72.0,
            score_interpretation="Good match — competitive candidate.",
            hiring_probability="Medium",
            full_report_markdown="# Report\n\nDetails here...",
        )
        assert fr.match_score == 72.0
        assert fr.hiring_probability == "Medium"

    def test_invalid_score(self):
        with pytest.raises(ValidationError):
            FinalReport(
                job_title="Test",
                executive_summary="Test",
                match_score=150.0,
                score_interpretation="Test",
                hiring_probability="High",
                full_report_markdown="# Test",
            )


class TestAnalysisResponse:
    def test_success_status(self):
        ar = AnalysisResponse(status="success")
        assert ar.status == "success"
        assert ar.processing_steps == []

    def test_error_status(self):
        ar = AnalysisResponse(status="error", error_message="Something went wrong")
        assert ar.error_message == "Something went wrong"


class TestWorkflowStep:
    def test_all_steps_defined(self):
        steps = list(WorkflowStep)
        assert WorkflowStep.RESUME_AGENT in steps
        assert WorkflowStep.END in steps
        assert len(steps) == 8  # 7 agents + END

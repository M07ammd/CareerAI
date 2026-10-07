"""
Evaluation dataset and basic metrics for CareerPilot AI.

This module provides:
1. Sample CV / job-description pairs
2. Basic evaluation functions to verify system behaviour
"""

from __future__ import annotations

from typing import List


SAMPLE_PAIRS = [
    {
        "name": "ML Engineer - Good Match",
        "resume_text": """
Alice Chen | alice.chen@email.com
LinkedIn: linkedin.com/in/alicechen

SUMMARY
Senior Machine Learning Engineer with 5 years of experience building
production ML systems. Expertise in PyTorch, scikit-learn, and LangChain.

EDUCATION
M.Sc. Computer Science | Stanford University | 2019

EXPERIENCE
ML Engineer | TechCorp | 2019–2024
- Designed and deployed NLP pipelines using transformers (BERT, GPT-2)
- Built LangChain-based agentic systems for document Q&A
- Implemented CI/CD for ML models using Docker and Kubernetes
- Led team of 3 engineers

TECHNICAL SKILLS
Python, PyTorch, TensorFlow, scikit-learn, LangChain, LangGraph,
HuggingFace Transformers, FastAPI, Docker, Kubernetes, PostgreSQL,
Redis, AWS (S3, EC2, SageMaker), Git

AI/ML EXPERIENCE
BERT, GPT-2, RAG, Agentic AI, Fine-tuning, MLflow, Weights & Biases

PROJECTS
- ResumeParser: NLP pipeline for structured extraction from CVs
- DocAgent: LangGraph agent for multi-step document analysis
""",
        "job_description": """
Senior ML Engineer

We are looking for a Senior ML Engineer to join our AI team.

REQUIRED:
- 5+ years of experience in ML/AI
- Strong Python programming skills
- Experience with PyTorch or TensorFlow
- LangChain or LangGraph experience
- FastAPI for building ML APIs
- Docker and container orchestration

PREFERRED:
- Experience with LLMs and prompt engineering
- Kubernetes experience
- Cloud platforms (AWS/GCP/Azure)

RESPONSIBILITIES:
- Design and implement ML pipelines
- Build agentic AI systems
- Deploy models to production
- Collaborate with product teams
""",
        "expected_match_score_min": 75,
        "expected_missing_skills": [],  # Should be a good match
        "expected_matched_min": 6,
    },
    {
        "name": "ML Engineer - Moderate Match",
        "resume_text": """
Bob Martinez | bob@email.com

SUMMARY
Backend developer transitioning to ML. 3 years Python experience.
Built REST APIs with FastAPI. Learning ML on the side.

EDUCATION
B.Sc. Software Engineering | University of Madrid | 2021

EXPERIENCE
Backend Developer | StartupXYZ | 2021–2024
- Built REST APIs with FastAPI and Django
- PostgreSQL, Redis, Docker
- Basic Python scripting and automation

SKILLS
Python, FastAPI, Django, PostgreSQL, Redis, Docker, REST APIs, Git
Currently learning: PyTorch, scikit-learn basics
""",
        "job_description": """
ML Engineer Position

Requirements:
- 3+ years Python
- PyTorch or TensorFlow (required)
- Experience with NLP models
- LangChain experience required
- MLOps experience (MLflow, DVC)
- Docker and Kubernetes

Nice to have:
- FastAPI experience
- Cloud experience
""",
        "expected_match_score_min": 25,
        "expected_match_score_max": 65,
        "expected_missing_skills_min": 3,  # Should identify several gaps
    },
    {
        "name": "Data Scientist - Domain Mismatch",
        "resume_text": """
Carol Johnson | carol@email.com

SUMMARY
Data Scientist with 4 years experience in statistical analysis and
business intelligence. Expert in R, SQL, Tableau.

EDUCATION
M.Sc. Statistics | UCL | 2020

EXPERIENCE
Data Scientist | BigRetail Co | 2020–2024
- Statistical analysis of customer behaviour data using R
- Built Tableau dashboards for C-suite reporting
- SQL query optimisation
- A/B testing and experimental design

SKILLS
R, SQL, Tableau, Excel, SPSS, SAS, Power BI
Basic Python (pandas, matplotlib)
""",
        "job_description": """
Senior ML Engineer - NLP Focus

Requirements:
- Python (expert level required)
- PyTorch or TensorFlow
- NLP: BERT, transformers, LLMs
- LangChain / LangGraph
- Production ML deployment
- Docker, Kubernetes, CI/CD
- 5+ years ML engineering experience
""",
        "expected_match_score_max": 35,  # Should be a poor match
        "expected_missing_skills_min": 5,
    },
]


def check_score_in_range(
    score: float,
    min_score: float | None = None,
    max_score: float | None = None,
) -> bool:
    """Check if a match score falls within expected bounds."""
    if min_score is not None and score < min_score:
        return False
    if max_score is not None and score > max_score:
        return False
    return True


def check_missing_skills_count(
    missing_skills: List[str],
    min_count: int | None = None,
    max_count: int | None = None,
) -> bool:
    """Check if missing skills count is within expected bounds."""
    count = len(missing_skills)
    if min_count is not None and count < min_count:
        return False
    if max_count is not None and count > max_count:
        return False
    return True


def evaluate_structured_output_validity(result: dict) -> dict:
    """
    Check that all expected structured outputs are present and valid.

    Args:
        result: The AnalysisResponse as a dictionary.

    Returns:
        Dictionary with validity checks.
    """
    checks = {}

    checks["has_resume_analysis"] = result.get("resume_analysis") is not None
    checks["has_job_analysis"] = result.get("job_analysis") is not None
    checks["has_skill_match"] = result.get("skill_match") is not None
    checks["has_skill_gaps"] = result.get("skill_gaps") is not None
    checks["has_interview_questions"] = result.get("interview_questions") is not None
    checks["has_career_roadmap"] = result.get("career_roadmap") is not None
    checks["has_final_report"] = result.get("final_report") is not None

    if result.get("skill_match"):
        score = result["skill_match"].get("match_score", -1)
        checks["match_score_in_range"] = 0 <= score <= 100

    if result.get("final_report"):
        checks["has_report_markdown"] = bool(
            result["final_report"].get("full_report_markdown", "")
        )

    checks["overall_valid"] = all(checks.values())
    return checks


# ---------------------------------------------------------------------------
# Pytest-based evaluation tests
# ---------------------------------------------------------------------------

import pytest


class TestEvaluationDataset:
    def test_sample_pairs_structure(self):
        """All sample pairs have required keys."""
        for pair in SAMPLE_PAIRS:
            assert "name" in pair
            assert "resume_text" in pair
            assert "job_description" in pair
            assert len(pair["resume_text"]) > 50
            assert len(pair["job_description"]) > 50

    def test_score_range_logic(self):
        """Test the evaluation helper functions."""
        assert check_score_in_range(75.0, min_score=60) is True
        assert check_score_in_range(40.0, min_score=60) is False
        assert check_score_in_range(40.0, max_score=50) is True
        assert check_score_in_range(60.0, max_score=50) is False
        assert check_score_in_range(50.0, min_score=40, max_score=60) is True

    def test_missing_skills_count_logic(self):
        skills = ["Python", "Docker", "Kubernetes"]
        assert check_missing_skills_count(skills, min_count=2) is True
        assert check_missing_skills_count(skills, min_count=5) is False
        assert check_missing_skills_count(skills, max_count=5) is True
        assert check_missing_skills_count(skills, max_count=2) is False

    def test_structured_output_validity_all_present(self):
        mock_result = {
            "resume_analysis": {"summary": "Test"},
            "job_analysis": {"job_title": "Engineer"},
            "skill_match": {"match_score": 70},
            "skill_gaps": {"overall_gap_summary": "Some gaps"},
            "interview_questions": {"technical_questions": []},
            "career_roadmap": {"career_trajectory": "Path"},
            "final_report": {"full_report_markdown": "# Report"},
        }
        checks = evaluate_structured_output_validity(mock_result)
        assert checks["has_resume_analysis"] is True
        assert checks["has_skill_match"] is True
        assert checks["match_score_in_range"] is True
        assert checks["has_report_markdown"] is True

    def test_structured_output_validity_missing_fields(self):
        mock_result = {
            "resume_analysis": None,
            "job_analysis": None,
        }
        checks = evaluate_structured_output_validity(mock_result)
        assert checks["has_resume_analysis"] is False
        assert checks["overall_valid"] is False

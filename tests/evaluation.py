"""
CareerPilot AI — Evaluation Harness (Phase 4)

Usage:
  # Full evaluation with a real API key (not run in CI by default):
  python tests/evaluation.py --runs 5

  # CI-safe dry run using a fake LLM:
  python tests/evaluation.py --dry-run

  # Run only the pytest-based unit checks:
  pytest tests/evaluation.py

The labeled pairs are stored in tests/eval_pairs.json.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import List, Optional

# ── Path setup so we can import from the app package ─────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Helpers ───────────────────────────────────────────────────────────────────


def check_score_in_range(
    score: float,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
) -> bool:
    """Return True if *score* falls within [min_score, max_score]."""
    if min_score is not None and score < min_score:
        return False
    if max_score is not None and score > max_score:
        return False
    return True


def check_missing_skills_count(
    missing_skills: List[str],
    min_count: Optional[int] = None,
    max_count: Optional[int] = None,
) -> bool:
    count = len(missing_skills)
    if min_count is not None and count < min_count:
        return False
    if max_count is not None and count > max_count:
        return False
    return True


def evaluate_structured_output_validity(result: dict) -> dict:
    """Check that all expected structured outputs are present and valid."""
    checks: dict[str, bool] = {}
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


# ── Labeled pairs (inline; also written to eval_pairs.json on first run) ─────

EVAL_PAIRS = [
    {
        "name": "ML Engineer — Perfect Match",
        "resume_text": """
Alice Chen | alice.chen@email.com

SUMMARY
Senior Machine Learning Engineer with 5 years of experience building production ML systems.
Expertise in PyTorch, scikit-learn, LangChain, and LangGraph.

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
""",
        "expected_score_min": 75,
        "expected_score_max": 100,
        "expected_missing_max": 2,
    },
    {
        "name": "ML Engineer — Moderate Match (Backend Transition)",
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
        "expected_score_min": 20,
        "expected_score_max": 65,
        "expected_missing_min": 3,
    },
    {
        "name": "Data Scientist — Domain Mismatch (Statistical → ML Engineering)",
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
Senior ML Engineer — NLP Focus

Requirements:
- Python (expert level required)
- PyTorch or TensorFlow
- NLP: BERT, transformers, LLMs
- LangChain / LangGraph
- Production ML deployment
- Docker, Kubernetes, CI/CD
- 5+ years ML engineering experience
""",
        "expected_score_max": 35,
        "expected_missing_min": 5,
    },
    {
        "name": "DevOps Engineer — Completely Wrong Domain",
        "resume_text": """
Dave Lee | dave@email.com

SUMMARY
Senior DevOps Engineer with 6 years experience in infrastructure and CI/CD.
Expert in Terraform, Ansible, Jenkins, and cloud platforms.

EDUCATION
B.Sc. Computer Networks | UCL | 2018

EXPERIENCE
DevOps Engineer | CloudOps Inc | 2018–2024
- Managed AWS infrastructure (EC2, S3, EKS) using Terraform
- Implemented GitLab CI/CD pipelines for 20+ microservices
- Kubernetes cluster management and monitoring (Prometheus, Grafana)
- Docker containerisation of legacy applications

SKILLS
Terraform, Ansible, Jenkins, Docker, Kubernetes, AWS, GCP, Azure,
Bash, Python (scripting only), Git, Linux
""",
        "job_description": """
Senior Data Scientist — Computer Vision

Requirements:
- Python (expert level, 5+ years)
- PyTorch or TensorFlow for deep learning
- Computer vision: CNNs, object detection, YOLO, OpenCV
- Experience with model training on GPU clusters
- MLflow or DVC for experiment tracking
- Familiarity with Hugging Face
- Strong statistics and probability background
""",
        "expected_score_max": 20,
        "expected_missing_min": 6,
    },
    {
        "name": "Full Stack Developer — Frontend Applying for Backend Python",
        "resume_text": """
Eve Wilson | eve@email.com

SUMMARY
Full Stack Developer with 4 years experience. Specialises in React,
TypeScript, and Node.js. Some Python scripting experience.

EDUCATION
B.Sc. Computer Science | University of Edinburgh | 2020

EXPERIENCE
Full Stack Developer | WebAgency | 2020–2024
- Built React/TypeScript SPAs with REST API integrations
- Node.js backend APIs with Express
- PostgreSQL and MongoDB
- Basic Python scripting for data processing scripts

SKILLS
React, TypeScript, JavaScript, Node.js, Express, PostgreSQL,
MongoDB, HTML/CSS, Git, Docker (basic)
""",
        "job_description": """
Senior Python Backend Engineer

Requirements:
- Python 3.10+ (5+ years, expert level)
- Django or FastAPI framework
- PostgreSQL and Redis
- Async programming (asyncio, celery)
- REST and GraphQL APIs
- Docker and Kubernetes
- CI/CD pipelines
- Strong knowledge of design patterns
""",
        "expected_score_min": 15,
        "expected_score_max": 50,
        "expected_missing_min": 3,
    },
    {
        "name": "Junior Dev — Entry Level Applying Senior Role",
        "resume_text": """
Frank Nguyen | frank@email.com

SUMMARY
Recent Computer Science graduate with internship experience.
Enthusiastic about Python and machine learning.

EDUCATION
B.Sc. Computer Science | University of Manchester | 2024

EXPERIENCE
Software Intern | SmallStartup | Summer 2023 (3 months)
- Wrote Python scripts for data cleaning
- Fixed bugs in Flask REST API
- Basic SQL queries

SKILLS
Python (beginner), SQL, Flask (basic), Git
Learning: PyTorch, scikit-learn
""",
        "job_description": """
Senior ML Engineer — 5+ Years Required

Requirements:
- 5+ years Python (expert)
- PyTorch or TensorFlow (production experience)
- LangChain, LangGraph
- Kubernetes, Docker
- AWS or GCP
- MLflow, experiment tracking
- Experience managing ML teams
""",
        "expected_score_max": 25,
        "expected_missing_min": 5,
    },
]


# ── Fake LLM for CI-safe dry-run ──────────────────────────────────────────────


class FakeLLMForEval:
    """
    Returns plausible AnalysisResponse instances without calling a real LLM.
    Used so the evaluation harness itself is testable in CI.
    """

    async def run(self, resume_text: str, job_description: str):
        from app.schemas.models import (
            AnalysisResponse, ResumeAnalysis, JobAnalysis, SkillMatch,
        )
        # Deterministic fake scoring based on keyword overlap
        resume_words = set(resume_text.lower().split())
        jd_words = set(job_description.lower().split())
        overlap = len(resume_words & jd_words)
        score = min(100, int(overlap * 2))

        return AnalysisResponse(
            status="success",
            resume_analysis=ResumeAnalysis(
                summary="Extracted from fake LLM.",
                technical_skills=list(resume_words)[:5],
            ),
            job_analysis=JobAnalysis(
                job_title="Extracted Role",
                required_skills=list(jd_words)[:5],
                domain="Engineering",
                seniority_level="Mid",
            ),
            skill_match=SkillMatch(
                matched_skills=list(resume_words & jd_words)[:5],
                missing_skills=list(jd_words - resume_words)[:5],
                match_score=score,
                explanation="Fake LLM deterministic match.",
            ),
            processing_steps=["resume_agent", "job_agent", "skill_agent"],
        )


# ── Real evaluation runner ────────────────────────────────────────────────────


async def run_pair_n_times(pair: dict, n: int = 5, dry_run: bool = False) -> dict:
    """Run a single eval pair N times and collect score statistics."""
    scores = []
    missing_counts = []
    failures = 0

    for run_idx in range(n):
        try:
            if dry_run:
                fake = FakeLLMForEval()
                result = await fake.run(pair["resume_text"], pair["job_description"])
                score = result.skill_match.match_score if result.skill_match else -1
                missing = len(result.skill_match.missing_skills) if result.skill_match else 0
            else:
                from app.services.analysis_service import run_analysis
                result = await run_analysis(
                    resume_text=pair["resume_text"],
                    job_description=pair["job_description"],
                    request_id=f"eval-{pair['name'][:10]}-run-{run_idx}",
                )
                score = (
                    result.skill_match.match_score
                    if result.skill_match
                    else -1
                )
                missing = (
                    len(result.skill_match.missing_skills)
                    if result.skill_match
                    else 0
                )

            if score >= 0:
                scores.append(score)
                missing_counts.append(missing)
            else:
                failures += 1
        except Exception as exc:
            print(f"  [FAIL] Run {run_idx}: {exc}")
            failures += 1

    return {
        "name": pair["name"],
        "runs": n,
        "failures": failures,
        "scores": scores,
        "mean": statistics.mean(scores) if scores else None,
        "std": statistics.stdev(scores) if len(scores) > 1 else 0,
        "expected_score_min": pair.get("expected_score_min"),
        "expected_score_max": pair.get("expected_score_max"),
        "expected_missing_min": pair.get("expected_missing_min"),
        "expected_missing_max": pair.get("expected_missing_max"),
        "score_in_range": (
            check_score_in_range(
                statistics.mean(scores) if scores else -1,
                pair.get("expected_score_min"),
                pair.get("expected_score_max"),
            )
            if scores
            else False
        ),
        "missing_count_ok": (
            check_missing_skills_count(
                ["x"] * (int(statistics.mean(missing_counts)) if missing_counts else 0),
                pair.get("expected_missing_min"),
                pair.get("expected_missing_max"),
            )
            if missing_counts
            else True
        ),
    }


def print_summary_table(results: list[dict]) -> None:
    """Print a human-readable summary table."""
    cols = ["Name", "Runs", "Fail", "Mean", "Std", "Expected Range", "Pass"]
    widths = [35, 5, 5, 6, 6, 20, 6]
    header = "  ".join(c.ljust(w) for c, w in zip(cols, widths))
    print("\n" + "=" * len(header))
    print("CareerPilot AI — Evaluation Report")
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    all_pass = True
    for r in results:
        name = r["name"][:widths[0]]
        runs = str(r["runs"])
        fail = str(r["failures"])
        mean = f"{r['mean']:.1f}" if r["mean"] is not None else "N/A"
        std = f"{r['std']:.1f}"
        lo = r.get("expected_score_min", "?")
        hi = r.get("expected_score_max", "?")
        exp_range = f"[{lo}, {hi}]"
        passed = r["score_in_range"] and r["missing_count_ok"]
        ok = "✓" if passed else "✗"
        if not passed:
            all_pass = False
        row = "  ".join(
            v.ljust(w) for v, w in zip(
                [name, runs, fail, mean, std, exp_range, ok], widths
            )
        )
        print(row)

    print("=" * len(header))
    print(f"Overall: {'ALL PASS ✓' if all_pass else 'SOME FAILURES ✗'}")
    print()


async def main(n_runs: int = 5, dry_run: bool = False) -> None:
    # Save eval pairs to JSON (useful for external tooling)
    pairs_path = Path(__file__).parent / "eval_pairs.json"
    if not pairs_path.exists():
        with open(pairs_path, "w") as f:
            json.dump(EVAL_PAIRS, f, indent=2)
        print(f"Saved {len(EVAL_PAIRS)} eval pairs to {pairs_path}")

    print(f"\nRunning evaluation — {n_runs} runs per pair — dry_run={dry_run}")
    if dry_run:
        print("  (Using fake LLM — no real API calls)")

    results = []
    for pair in EVAL_PAIRS:
        print(f"  [{pair['name']}]")
        t0 = time.time()
        res = await run_pair_n_times(pair, n=n_runs, dry_run=dry_run)
        elapsed = time.time() - t0
        status = "✓" if (res["score_in_range"] and res["missing_count_ok"]) else "✗"
        mean_str = f"{res['mean']:.1f}" if res["mean"] is not None else "N/A"
        print(f"    Mean score: {mean_str} (std: {res['std']:.1f}) — {status} [{elapsed:.1f}s]")
        results.append(res)

    print_summary_table(results)

    # Exit with non-zero if any pair fails
    failed = [r for r in results if not (r["score_in_range"] and r["missing_count_ok"])]
    if failed and not dry_run:
        sys.exit(1)


# ── Pytest-based unit checks (always run in CI) ───────────────────────────────

import pytest


class TestEvaluationDataset:
    def test_eval_pairs_structure(self):
        """All eval pairs have required keys and non-empty content."""
        for pair in EVAL_PAIRS:
            assert "name" in pair
            assert "resume_text" in pair
            assert "job_description" in pair
            assert len(pair["resume_text"].strip()) > 50, f"{pair['name']}: resume too short"
            assert len(pair["job_description"].strip()) > 50, f"{pair['name']}: JD too short"
            # Must have at least one bound
            has_score_bound = "expected_score_min" in pair or "expected_score_max" in pair
            assert has_score_bound, f"{pair['name']}: needs a score bound"

    def test_score_range_helper(self):
        assert check_score_in_range(75.0, min_score=60) is True
        assert check_score_in_range(40.0, min_score=60) is False
        assert check_score_in_range(40.0, max_score=50) is True
        assert check_score_in_range(60.0, max_score=50) is False
        assert check_score_in_range(50.0, min_score=40, max_score=60) is True

    def test_missing_skills_count_helper(self):
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
        mock_result = {"resume_analysis": None, "job_analysis": None}
        checks = evaluate_structured_output_validity(mock_result)
        assert checks["has_resume_analysis"] is False
        assert checks["overall_valid"] is False

    @pytest.mark.asyncio
    async def test_dry_run_ci_variant(self):
        """Run the eval harness with the fake LLM — no real API keys needed."""
        pair = EVAL_PAIRS[0]
        result = await run_pair_n_times(pair, n=2, dry_run=True)
        assert result["runs"] == 2
        assert result["failures"] == 0
        assert result["mean"] is not None
        assert 0 <= result["mean"] <= 100

    @pytest.mark.asyncio
    async def test_dry_run_all_pairs_no_crash(self):
        """The harness must not crash on any eval pair in dry-run mode."""
        for pair in EVAL_PAIRS:
            result = await run_pair_n_times(pair, n=1, dry_run=True)
            assert result["failures"] == 0, f"Pair '{pair['name']}' crashed in dry-run"


# ── CLI entrypoint ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CareerPilot AI Evaluation Harness")
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runs per eval pair (default: 5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use fake LLM (no API keys required, CI-safe)",
    )
    args = parser.parse_args()
    asyncio.run(main(n_runs=args.runs, dry_run=args.dry_run))

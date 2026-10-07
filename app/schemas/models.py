"""
CareerPilot AI - Pydantic Schemas / Data Models

All structured output models used by agents and the API.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SkillPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MatchLevel(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    MISSING = "missing"


class WorkflowStep(str, Enum):
    RESUME_AGENT = "resume_agent"
    JOB_AGENT = "job_agent"
    SKILL_AGENT = "skill_agent"
    GAP_AGENT = "gap_agent"
    INTERVIEW_AGENT = "interview_agent"
    ROADMAP_AGENT = "roadmap_agent"
    REPORT_AGENT = "report_agent"
    END = "end"


# ---------------------------------------------------------------------------
# Resume Analysis
# ---------------------------------------------------------------------------


class EducationEntry(BaseModel):
    degree: str = Field(description="Degree title, e.g. B.Sc. Computer Science")
    institution: str = Field(description="University or institution name")
    year: Optional[str] = Field(default=None, description="Graduation year or range")
    gpa: Optional[str] = Field(default=None, description="GPA if mentioned")


class ExperienceEntry(BaseModel):
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    duration: Optional[str] = Field(default=None, description="Duration, e.g. 2021–2023")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")


class ProjectEntry(BaseModel):
    name: str = Field(description="Project name")
    description: str = Field(description="Brief description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    highlights: List[str] = Field(default_factory=list, description="Key achievements or features")


class ResumeAnalysis(BaseModel):
    candidate_name: Optional[str] = Field(default=None, description="Candidate full name")
    contact_email: Optional[str] = Field(default=None, description="Email address")
    summary: str = Field(description="2-3 sentence professional summary of the candidate")
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list, description="All technical skills found")
    soft_skills: List[str] = Field(default_factory=list, description="Soft/interpersonal skills found")
    ai_ml_experience: List[str] = Field(
        default_factory=list,
        description="Specific AI/ML/NLP technologies and frameworks the candidate has used",
    )
    total_experience_years: Optional[float] = Field(
        default=None, description="Estimated total professional experience in years"
    )
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    certifications: List[str] = Field(default_factory=list, description="Certifications or courses")


# ---------------------------------------------------------------------------
# Job Analysis
# ---------------------------------------------------------------------------


class JobAnalysis(BaseModel):
    job_title: str = Field(description="The job title being analyzed")
    company: Optional[str] = Field(default=None, description="Company name if mentioned")
    required_skills: List[str] = Field(default_factory=list, description="Must-have skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have skills")
    required_experience_years: Optional[float] = Field(
        default=None, description="Minimum years of experience required"
    )
    responsibilities: List[str] = Field(default_factory=list, description="Key job responsibilities")
    technologies: List[str] = Field(default_factory=list, description="All technologies mentioned")
    domain: str = Field(description="Domain area, e.g. ML Engineering, Backend, Data Science")
    seniority_level: str = Field(
        description="Seniority level: Junior / Mid / Senior / Lead / Staff"
    )
    key_qualifications: List[str] = Field(
        default_factory=list, description="Most important qualifications distilled"
    )


# ---------------------------------------------------------------------------
# Skill Matching
# ---------------------------------------------------------------------------


class SkillMatchDetail(BaseModel):
    skill: str = Field(description="The skill name")
    level: MatchLevel = Field(description="Whether it is a full, partial, or missing match")
    notes: Optional[str] = Field(default=None, description="Explanation for partial or full match")


class SkillMatch(BaseModel):
    matched_skills: List[str] = Field(default_factory=list, description="Skills the candidate has")
    missing_skills: List[str] = Field(
        default_factory=list, description="Skills required but absent from resume"
    )
    partially_matched_skills: List[SkillMatchDetail] = Field(
        default_factory=list, description="Skills the candidate has some exposure to"
    )
    match_score: int = Field(
        ge=0, le=100, description="Overall match score from 0 to 100"
    )
    explanation: str = Field(description="Narrative explanation of the match score")
    strengths: List[str] = Field(
        default_factory=list, description="Areas where the candidate excels vs the job"
    )
    weaknesses: List[str] = Field(
        default_factory=list, description="Areas where the candidate falls short"
    )


# ---------------------------------------------------------------------------
# Skill Gap Analysis
# ---------------------------------------------------------------------------


class SkillGapItem(BaseModel):
    skill: str = Field(description="Missing skill name")
    priority: SkillPriority = Field(description="Priority level: high / medium / low")
    reason: str = Field(description="Why this gap matters for the role")
    learning_resources: List[str] = Field(
        default_factory=list, description="Suggested resources or learning paths"
    )
    estimated_learning_time: Optional[str] = Field(
        default=None, description="Rough time estimate to learn this skill, e.g. '2–4 weeks'"
    )


class SkillGaps(BaseModel):
    high_priority_gaps: List[SkillGapItem] = Field(default_factory=list)
    medium_priority_gaps: List[SkillGapItem] = Field(default_factory=list)
    low_priority_gaps: List[SkillGapItem] = Field(default_factory=list)
    overall_gap_summary: str = Field(description="Overall narrative summary of the skill gaps")
    critical_blockers: List[str] = Field(
        default_factory=list,
        description="Skills without which the candidate cannot get the job",
    )


# ---------------------------------------------------------------------------
# Interview Questions
# ---------------------------------------------------------------------------


class InterviewQuestion(BaseModel):
    question: str = Field(description="The interview question")
    category: str = Field(description="Category: Technical / Behavioral / Project-based / HR")
    rationale: str = Field(description="Why this question is relevant given the CV and JD")
    suggested_answer_points: List[str] = Field(
        default_factory=list, description="Key points the candidate should address"
    )


class InterviewQuestions(BaseModel):
    technical_questions: List[InterviewQuestion] = Field(default_factory=list)
    project_questions: List[InterviewQuestion] = Field(default_factory=list)
    behavioral_questions: List[InterviewQuestion] = Field(default_factory=list)
    hr_questions: List[InterviewQuestion] = Field(default_factory=list)
    preparation_tips: List[str] = Field(
        default_factory=list, description="General interview preparation tips"
    )


# ---------------------------------------------------------------------------
# Career Roadmap
# ---------------------------------------------------------------------------


class RoadmapMilestone(BaseModel):
    title: str = Field(description="Milestone title")
    description: str = Field(description="What to achieve at this milestone")
    action_items: List[str] = Field(default_factory=list, description="Concrete steps to take")
    resources: List[str] = Field(
        default_factory=list, description="Courses, books, or links to learn from"
    )
    timeframe: str = Field(description="Recommended timeframe, e.g. 'Week 1–2'")
    success_metrics: List[str] = Field(
        default_factory=list, description="How to know you've achieved this milestone"
    )


class CareerRoadmap(BaseModel):
    immediate_actions: List[RoadmapMilestone] = Field(
        default_factory=list, description="Actions to take in the next 0–2 weeks"
    )
    short_term_goals: List[RoadmapMilestone] = Field(
        default_factory=list, description="Goals to reach in 1–3 months"
    )
    long_term_goals: List[RoadmapMilestone] = Field(
        default_factory=list, description="Goals to reach in 3–12 months"
    )
    recommended_projects: List[str] = Field(
        default_factory=list, description="Portfolio projects to build"
    )
    recommended_certifications: List[str] = Field(
        default_factory=list, description="Certifications worth pursuing"
    )
    career_trajectory: str = Field(
        description="Narrative of the recommended career trajectory"
    )


# ---------------------------------------------------------------------------
# Final Report
# ---------------------------------------------------------------------------


class FinalReport(BaseModel):
    candidate_name: Optional[str] = Field(default=None)
    job_title: str = Field(description="Job title being applied for")
    executive_summary: str = Field(description="3-5 sentence executive summary")
    match_score: int = Field(ge=0, le=100, description="Overall match score")
    score_interpretation: str = Field(
        description="What the score means and what it implies"
    )
    key_strengths: List[str] = Field(default_factory=list)
    critical_gaps: List[str] = Field(default_factory=list)
    top_recommendations: List[str] = Field(
        default_factory=list, description="Top 5 actionable recommendations"
    )
    hiring_probability: str = Field(
        description="Estimated likelihood of success: Low / Medium / High"
    )
    next_steps: List[str] = Field(default_factory=list, description="Immediate next steps")
    full_report_markdown: str = Field(
        description="Complete professional report in Markdown format"
    )


# ---------------------------------------------------------------------------
# API Request / Response Models
# ---------------------------------------------------------------------------


class AnalysisRequest(BaseModel):
    job_description: str = Field(min_length=50, max_length=15_000, description="The full job description text")


class AnalysisResponse(BaseModel):
    status: str = Field(description="'success', 'partial', or 'error'")
    resume_analysis: Optional[ResumeAnalysis] = None
    job_analysis: Optional[JobAnalysis] = None
    skill_match: Optional[SkillMatch] = None
    skill_gaps: Optional[SkillGaps] = None
    interview_questions: Optional[InterviewQuestions] = None
    career_roadmap: Optional[CareerRoadmap] = None
    final_report: Optional[FinalReport] = None
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list, description="Warnings for failed optional sections")
    processing_steps: List[str] = Field(default_factory=list, description="Steps completed during processing")


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_provider: str

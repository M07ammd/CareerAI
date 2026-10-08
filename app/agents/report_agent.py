"""
CareerPilot AI - Report Generator Agent

Combines all agent results into a professional final report.
Uses the LLM only for a brief narrative summary.
Transient LLM errors propagate for RetryPolicy.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.agents.agent_runner import is_transient
from app.agents.prompt_utils import ANTI_INJECTION_INSTRUCTION, wrap_user_content
from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.schemas.models import CVBulletRewrite, FinalReport, WorkflowStep
from app.tools.file_writer import save_analysis_json, save_report_markdown

logger = logging.getLogger(__name__)


class ReportSummary(BaseModel):
    executive_summary: str = Field(description="3-5 sentence executive summary")
    score_interpretation: str = Field(description="What the score means and what it implies")
    hiring_probability: str = Field(description="Estimated likelihood of success: Low / Medium / High")
    cv_bullet_rewrites: list[CVBulletRewrite] = Field(
        default_factory=list,
        description="Suggested rewrites for 2-3 CV bullets to better align with the job",
    )


SYSTEM_PROMPT = (
    "You are a Senior Career Intelligence Analyst.\n\n"
    "Your task is to synthesize the provided analysis results into a brief, professional summary.\n\n"
    "Provide:\n"
    "1. Executive Summary (3-5 sentences covering key findings)\n"
    "2. Score interpretation (what the match score means for this candidate)\n"
    "3. Hiring probability assessment (Low / Medium / High) with justification\n"
    "4. CV Bullet Rewrites (2-3 suggestions improving existing bullet points)\n"
    + ANTI_INJECTION_INSTRUCTION
)


def _build_markdown(state: CareerPilotState, summary: ReportSummary) -> str:
    ra = state.get("resume_analysis")
    ja = state.get("job_analysis")
    sm = state.get("skill_match")
    sg = state.get("skill_gaps")
    cr = state.get("career_roadmap")

    cand_name = ra.candidate_name if ra and ra.candidate_name else "Candidate"
    job_title = ja.job_title if ja else "Role"
    score = sm.match_score if sm else 0

    md = f"# CareerPilot AI Report: {cand_name} for {job_title}\n\n"
    md += f"**Date**: {datetime.now().strftime('%B %d, %Y')}\n\n"
    md += f"## Executive Summary\n{summary.executive_summary}\n\n"
    md += f"## Match Score: {score}/100\n{summary.score_interpretation}\n\n"
    md += f"**Hiring Probability**: {summary.hiring_probability}\n\n"

    if sm and sm.strengths:
        md += "## Key Strengths\n"
        for s in sm.strengths:
            md += f"- {s}\n"
        md += "\n"

    if sg and sg.high_priority_gaps:
        md += "## Critical Gaps\n"
        for g in sg.high_priority_gaps:
            md += f"- **{g.skill}**: {g.reason}\n"
        md += "\n"

    if cr and cr.immediate_actions:
        md += "## Immediate Next Steps\n"
        for a in cr.immediate_actions:
            md += f"- **{a.title}**: {a.description}\n"
        md += "\n"

    if sm and sm.evidence_grounded_justification:
        md += "## Score Justification (Evidence-Grounded)\n"
        for ev in sm.evidence_grounded_justification:
            md += f"- {ev}\n"
        md += "\n"

    if summary.cv_bullet_rewrites:
        md += "## CV Bullet Rewrite Suggestions\n"
        for rewrite in summary.cv_bullet_rewrites:
            md += f"**Original**: *{rewrite.original_bullet}*\n\n"
            md += f"**Suggested**: {rewrite.suggested_bullet}\n\n"
            md += f"**Reasoning**: {rewrite.reasoning}\n\n"

    return md


async def report_agent(state: CareerPilotState) -> dict:
    """
    Generate the final consolidated report.
    Raises transient exceptions for LangGraph RetryPolicy.
    """
    logger.info("[ReportAgent] Generating final report")

    llm = get_structured_llm(ReportSummary)

    # Send only high-level stats to the LLM for the summary
    context: dict = {}
    if ra := state.get("resume_analysis"):
        context["candidate"] = ra.summary
        context["experience"] = [e.model_dump() for e in ra.experience]
    if ja := state.get("job_analysis"):
        context["job"] = ja.job_title
    if sm := state.get("skill_match"):
        context["score"] = sm.match_score

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Generate the summary based on:\n"
                + wrap_user_content("ANALYSIS DATA", json.dumps(context))
            )
        ),
    ]

    try:
        summary_result: ReportSummary = await llm.ainvoke(messages)

        sm = state.get("skill_match")
        sg = state.get("skill_gaps")
        cr = state.get("career_roadmap")
        ra = state.get("resume_analysis")
        ja = state.get("job_analysis")

        candidate_name = ra.candidate_name if ra and ra.candidate_name else "Candidate"
        job_title = ja.job_title if ja else "Role"
        key_strengths = sm.strengths if sm else []
        critical_gaps = [g.skill for g in sg.high_priority_gaps] if sg else []
        next_steps = [a.title for a in cr.immediate_actions] if cr else []
        top_recs = []
        if cr:
            top_recs = [a.title for a in cr.immediate_actions] + [a.title for a in cr.short_term_goals]
            top_recs = top_recs[:5]

        md = _build_markdown(state, summary_result)

        final_report = FinalReport(
            candidate_name=candidate_name,
            job_title=job_title,
            executive_summary=summary_result.executive_summary,
            match_score=sm.match_score if sm else 0,
            score_interpretation=summary_result.score_interpretation,
            key_strengths=key_strengths,
            critical_gaps=critical_gaps,
            top_recommendations=top_recs,
            hiring_probability=summary_result.hiring_probability,
            next_steps=next_steps,
            full_report_markdown=md,
            cv_bullet_rewrites=summary_result.cv_bullet_rewrites,
        )

        try:
            save_report_markdown(md, candidate_name)
            all_data = {
                "resume_analysis": state.get("resume_analysis", {}).model_dump() if state.get("resume_analysis") else None,
                "job_analysis": state.get("job_analysis", {}).model_dump() if state.get("job_analysis") else None,
                "skill_match": state.get("skill_match", {}).model_dump() if state.get("skill_match") else None,
                "skill_gaps": state.get("skill_gaps", {}).model_dump() if state.get("skill_gaps") else None,
                "final_report": final_report.model_dump(),
            }
            save_analysis_json(all_data, candidate_name)
        except Exception as save_exc:
            logger.warning("[ReportAgent] Could not save report to disk: %s", save_exc)

        logger.info(
            "[ReportAgent] Done. Score: %d | Probability: %s",
            final_report.match_score,
            final_report.hiring_probability,
        )
        return {
            "final_report": final_report,
            "completed_steps": [WorkflowStep.REPORT_AGENT],
            "processing_log": [
                f"ReportAgent completed. Final score: {final_report.match_score}/100. "
                f"Hiring probability: {final_report.hiring_probability}"
            ],
        }

    except Exception as exc:
        if is_transient(exc):
            logger.warning("[ReportAgent] Transient error (will retry): %s", exc)
            raise
        logger.exception("[ReportAgent] Non-retryable error: %s", exc)
        return {
            "errors": [{"step": WorkflowStep.REPORT_AGENT, "error": str(exc)}],
            "processing_log": [f"ReportAgent FAILED: {exc}"],
        }
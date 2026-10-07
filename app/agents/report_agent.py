"""
CareerPilot AI - Report Generator Agent

Combines all agent results into a single, professional final report.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import CareerPilotState
from app.llm import get_structured_llm
from app.schemas.models import FinalReport, WorkflowStep
from app.tools.file_writer import save_analysis_json, save_report_markdown

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Senior Career Intelligence Analyst producing a professional career report.

Your task is to synthesize ALL analysis results into one comprehensive, professional final report.

The report must include:
1. Executive Summary (3-5 sentences covering the key findings)
2. Match Score interpretation (what the number means for this candidate)
3. Key strengths (specific, not generic)
4. Critical gaps (honest assessment)
5. Top 5 actionable recommendations
6. Hiring probability assessment (Low / Medium / High) with justification
7. Immediate next steps

For full_report_markdown, produce a beautifully formatted Markdown document with:
- Proper headings and sections
- Tables for skills comparison
- Bullet points for recommendations
- A professional tone that is encouraging but honest
- At least 600 words of meaningful content

The report should feel like it was written by a human senior career coach, not a generic AI.
"""


def _build_context(state: CareerPilotState) -> str:
    """Assemble all analysis data into a single context string."""
    parts = []

    if ra := state.get("resume_analysis"):
        parts.append(f"=== RESUME ANALYSIS ===\n{json.dumps(ra.model_dump(), indent=2)}")

    if ja := state.get("job_analysis"):
        parts.append(f"=== JOB ANALYSIS ===\n{json.dumps(ja.model_dump(), indent=2)}")

    if sm := state.get("skill_match"):
        parts.append(f"=== SKILL MATCH ===\n{json.dumps(sm.model_dump(), indent=2)}")

    if sg := state.get("skill_gaps"):
        parts.append(f"=== SKILL GAPS ===\n{json.dumps(sg.model_dump(), indent=2)}")

    if iq := state.get("interview_questions"):
        # Keep concise for the context window
        q_count = (
            len(iq.technical_questions)
            + len(iq.project_questions)
            + len(iq.behavioral_questions)
            + len(iq.hr_questions)
        )
        parts.append(f"=== INTERVIEW QUESTIONS ===\nTotal generated: {q_count}")

    if cr := state.get("career_roadmap"):
        milestones = len(cr.immediate_actions) + len(cr.short_term_goals) + len(cr.long_term_goals)
        parts.append(
            f"=== CAREER ROADMAP ===\nTotal milestones: {milestones}\n"
            f"Trajectory: {cr.career_trajectory}"
        )

    parts.append(f"=== REPORT DATE ===\n{datetime.now().strftime('%B %d, %Y')}")
    return "\n\n".join(parts)


def report_agent(state: CareerPilotState) -> dict:
    """
    Generate the final comprehensive report.

    Args:
        state: Should contain all previous agent outputs.

    Returns:
        Partial state update with final_report populated.
    """
    logger.info("[ReportAgent] Generating final report")

    llm = get_structured_llm(FinalReport)
    context = _build_context(state)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                "Please generate the comprehensive final career report based on "
                "all the analysis below:\n\n" + context
            )
        ),
    ]

    try:
        result: FinalReport = llm.invoke(messages)

        # Persist report to disk (best-effort)
        try:
            candidate_name = result.candidate_name or "candidate"
            save_report_markdown(result.full_report_markdown, candidate_name)
            # Save full analysis JSON
            all_data = {
                "resume_analysis": state.get("resume_analysis", {}).model_dump()
                if state.get("resume_analysis")
                else None,
                "job_analysis": state.get("job_analysis", {}).model_dump()
                if state.get("job_analysis")
                else None,
                "skill_match": state.get("skill_match", {}).model_dump()
                if state.get("skill_match")
                else None,
                "skill_gaps": state.get("skill_gaps", {}).model_dump()
                if state.get("skill_gaps")
                else None,
                "final_report": result.model_dump(),
            }
            save_analysis_json(all_data, candidate_name)
        except Exception as save_exc:
            logger.warning("[ReportAgent] Could not save report to disk: %s", save_exc)

        logger.info(
            "[ReportAgent] Done. Score: %.1f | Probability: %s",
            result.match_score,
            result.hiring_probability,
        )
        return {
            "final_report": result,
            "completed_steps": [WorkflowStep.REPORT_AGENT],
            "processing_log": [
                f"ReportAgent completed. Final score: {result.match_score:.1f}/100. "
                f"Hiring probability: {result.hiring_probability}"
            ],
            "next_step": WorkflowStep.END,
        }

    except Exception as exc:
        logger.exception("[ReportAgent] LLM call failed: %s", exc)
        return {
            "errors": [
                {
                    "step": WorkflowStep.REPORT_AGENT,
                    "error": str(exc),
                    "retry_count": state.get("retry_counts", {}).get(
                        WorkflowStep.REPORT_AGENT, 0
                    ),
                }
            ],
            "processing_log": [f"ReportAgent FAILED: {exc}"],
            "next_step": WorkflowStep.END,
        }

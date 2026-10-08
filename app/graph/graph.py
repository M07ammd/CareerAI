"""
CareerPilot AI - LangGraph Workflow

Builds and compiles the StateGraph that orchestrates all agents.
"""

from __future__ import annotations

import logging

from langgraph.graph import END, START, StateGraph
from langgraph.pregel import RetryPolicy

from app.agents.gap_agent import gap_agent
from app.agents.interview_agent import interview_agent
from app.agents.job_agent import job_agent
from app.agents.report_agent import report_agent
from app.agents.resume_agent import resume_agent
from app.agents.roadmap_agent import roadmap_agent
from app.agents.skill_agent import skill_agent
from app.agents.cv_suggestion_agent import cv_suggestion_agent
from app.config import get_settings
from app.graph.state import CareerPilotState

def clean_state(state: CareerPilotState) -> dict:
    return {"web_search_results": [], "resume_text": ""}

logger = logging.getLogger(__name__)


def build_graph():
    """
    Build and compile the CareerPilot LangGraph workflow.

    Workflow:
        START
        ├──→ resume_agent ──┐
        └──→ job_agent    ──┴──→ skill_agent ──→ gap_agent ──┬──→ interview_agent ──┐
                                                             └──→ roadmap_agent   ──┴──→ report_agent ──→ cv_suggestion_agent ──→ END
    """
    settings = get_settings()
    builder = StateGraph(CareerPilotState)

    # Retry policy: max_attempts is retries + 1 (initial attempt)
    retry = RetryPolicy(
        initial_interval=1.0, 
        backoff_factor=2.0, 
        max_interval=10.0, 
        max_attempts=settings.max_agent_retries + 1,
        jitter=True
    )

    # ---- Register nodes ---------------------------------------------------
    builder.add_node("resume_agent", resume_agent, retry=retry)
    builder.add_node("job_agent", job_agent, retry=retry)
    builder.add_node("skill_agent", skill_agent, retry=retry)
    builder.add_node("gap_agent", gap_agent, retry=retry)
    builder.add_node("interview_agent", interview_agent, retry=retry)
    builder.add_node("roadmap_agent", roadmap_agent, retry=retry)
    builder.add_node("clean_state", clean_state)
    builder.add_node("report_agent", report_agent, retry=retry)
    builder.add_node("cv_suggestion_agent", cv_suggestion_agent, retry=retry)

    # ---- Graph Edges -------------------------------------------------------
    builder.add_edge(START, "resume_agent")
    builder.add_edge(START, "job_agent")

    # Fan-in: wait for both resume and job analysis before skill matching
    builder.add_edge(["resume_agent", "job_agent"], "skill_agent")

    builder.add_edge("skill_agent", "gap_agent")

    # Fan-out: interview prep and roadmap can be built in parallel from gap analysis
    builder.add_edge("gap_agent", "interview_agent")
    builder.add_edge("gap_agent", "roadmap_agent")

    # Fan-in: wait for both before cleaning state
    builder.add_edge(["interview_agent", "roadmap_agent"], "clean_state")
    builder.add_edge("clean_state", "report_agent")

    builder.add_edge("report_agent", "cv_suggestion_agent")
    builder.add_edge("cv_suggestion_agent", END)

    graph = builder.compile()
    logger.info("[Graph] CareerPilot workflow compiled successfully")
    return graph


# Module-level compiled graph (lazy-initialized)
_graph = None


def get_graph():
    """Return the compiled graph, building it on first call."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph

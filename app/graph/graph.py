"""
CareerPilot AI - LangGraph Workflow

Builds and compiles the StateGraph that orchestrates all agents.
"""

from __future__ import annotations

import logging

from langgraph.graph import END, START, StateGraph

from app.agents.gap_agent import gap_agent
from app.agents.interview_agent import interview_agent
from app.agents.job_agent import job_agent
from app.agents.report_agent import report_agent
from app.agents.resume_agent import resume_agent
from app.agents.roadmap_agent import roadmap_agent
from app.agents.skill_agent import skill_agent
from app.graph.router import supervisor_node, supervisor_router
from app.graph.state import CareerPilotState

logger = logging.getLogger(__name__)


def build_graph():
    """
    Build and compile the CareerPilot LangGraph workflow.

    Workflow:
        START
          ↓
        resume_agent   ──→  supervisor  ──→  job_agent
                                             ↓
                                          supervisor  ──→  skill_agent
                                                           ↓
                                                        supervisor  ──→  gap_agent
                                                                         ↓
                                                                      supervisor  ──→  interview_agent
                                                                                       ↓
                                                                                    supervisor  ──→  roadmap_agent
                                                                                                     ↓
                                                                                                  supervisor  ──→  report_agent
                                                                                                                   ↓
                                                                                                                  END

    Each agent sets state.next_step; the supervisor reads this to decide routing.
    The supervisor also handles retries via state.retry_counts.
    """
    builder = StateGraph(CareerPilotState)

    # ---- Register nodes ---------------------------------------------------
    builder.add_node("resume_agent", resume_agent)
    builder.add_node("job_agent", job_agent)
    builder.add_node("skill_agent", skill_agent)
    builder.add_node("gap_agent", gap_agent)
    builder.add_node("interview_agent", interview_agent)
    builder.add_node("roadmap_agent", roadmap_agent)
    builder.add_node("report_agent", report_agent)
    builder.add_node("supervisor", supervisor_node)

    # ---- Entry point -------------------------------------------------------
    builder.add_edge(START, "resume_agent")

    # ---- Agent → Supervisor edges ------------------------------------------
    # After each agent runs, control passes to the supervisor
    for agent_node in [
        "resume_agent",
        "job_agent",
        "skill_agent",
        "gap_agent",
        "interview_agent",
        "roadmap_agent",
        "report_agent",
    ]:
        builder.add_edge(agent_node, "supervisor")

    # ---- Supervisor conditional routing -----------------------------------
    # The supervisor inspects state.next_step and routes accordingly
    builder.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "resume_agent": "resume_agent",
            "job_agent": "job_agent",
            "skill_agent": "skill_agent",
            "gap_agent": "gap_agent",
            "interview_agent": "interview_agent",
            "roadmap_agent": "roadmap_agent",
            "report_agent": "report_agent",
            "__end__": END,
        },
    )

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

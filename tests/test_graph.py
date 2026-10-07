"""
Tests for the LangGraph workflow.
"""

import pytest

from app.graph.graph import get_graph
from app.graph.state import CareerPilotState, get_initial_state
from app.schemas.models import WorkflowStep


class TestGraphStructure:
    def test_graph_nodes_and_edges(self):
        graph = get_graph()
        # Verify that graph builds and returns a CompiledStateGraph
        assert graph is not None

class TestGetInitialState:
    def test_initial_state_structure(self):
        state = get_initial_state("My CV text", "Job description text")
        assert state["resume_text"] == "My CV text"
        assert state["job_description"] == "Job description text"
        assert state["resume_analysis"] is None
        assert state["completed_steps"] == []
        assert state["errors"] == []

    def test_initial_state_defaults(self):
        state = get_initial_state("CV", "JD")
        assert state["web_search_results"] == []
        assert len(state["processing_log"]) >= 1

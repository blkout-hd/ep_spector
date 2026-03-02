"""
Smoke tests for PipelineState TypedDict and pipeline graph construction
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "python"))


def test_pipeline_state_import():
    from pipeline.state import PipelineState
    state: PipelineState = {
        "source_urls": ["https://example.com"],
        "use_tor": False,
        "gpu_tier": "cpu",
        "run_id": "test-001",
        "documents": [],
        "entities": [],
        "embeddings": [],
        "media_probes": [],
        "errors": [],
        "kg_nodes_written": 0,
        "kg_edges_written": 0,
        "stage": "init",
        "complete": False,
    }
    assert state["gpu_tier"] == "cpu"


def test_pipeline_graph_builds():
    """StateGraph should compile without error."""
    try:
        from pipeline.graph import build_graph
        g = build_graph()
        assert g is not None
    except ImportError as e:
        import pytest
        pytest.skip(f"langgraph not installed: {e}")

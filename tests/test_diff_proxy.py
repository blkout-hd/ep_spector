"""
Smoke tests for diff_proxy_agent (suppression scoring)
No external dependencies required.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))


def test_suppression_score_computed(minimal_state):
    """Documents with both visible and hidden embeddings get a score."""
    from diff_proxy_agent import run
    result = run(minimal_state)
    assert "suppression_scores" in result
    assert "testdoc0001" in result["suppression_scores"]
    score = result["suppression_scores"]["testdoc0001"]
    assert isinstance(score, float)
    assert score >= 0.0


def test_no_hidden_embedding_no_score():
    """Documents with only visible embedding get no score."""
    from diff_proxy_agent import run
    state = {
        "embeddings": [
            {
                "embed_id": "e1",
                "source_id": "doc_x",
                "source_type": "document",
                "vector": [0.1] * 384,
                "layer": "visible",
            }
        ]
    }
    result = run(state)
    assert result["suppression_scores"] == {} or "doc_x" not in result["suppression_scores"]


def test_identical_layers_score_zero():
    """Identical visible and hidden layers should yield score ~0."""
    from diff_proxy_agent import run
    vec = [0.5] * 384
    state = {
        "embeddings": [
            {"embed_id": "v", "source_id": "doc_z", "source_type": "document",
             "vector": vec, "layer": "visible"},
            {"embed_id": "h", "source_id": "doc_z", "source_type": "document",
             "vector": vec, "layer": "hidden"},
        ]
    }
    result = run(state)
    assert result["suppression_scores"]["doc_z"] < 1e-6

"""
tests/test_pipeline_graph.py

Unit and smoke tests for agents/pipeline/graph.py.

Philosophy:
- We never call real agents (spaCy / PyMuPDF / Neo4j / etc.).
- Each node function is tested by patching its agent import and
  verifying state key mutations.
- build_graph() is tested for structural correctness only
  (node names, compile success, checkpointer wiring).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_state(**overrides) -> dict:
    base = {
        "source": "https://example.com/test.pdf",
        "doc_id": None,
        "visible_text": "",
        "hidden_text": "",
        "ocr_text": "",
        "has_hidden_text": False,
        "file_hash": "",
        "page_count": 0,
        "entities": [],
        "entity_count": 0,
        "doc_embedding": None,
        "entity_embeddings": {},
        "kg_node_ids": {},
        "kg_edges_written": 0,
        "cluster_labels": None,
        "n_clusters": 0,
        "error": None,
        "completed_stages": [],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# build_graph structural tests
# ---------------------------------------------------------------------------

class TestBuildGraph:
    def test_compiles_without_checkpointer(self):
        """build_graph() with no args returns a compiled graph."""
        from agents.pipeline.graph import build_graph
        g = build_graph()
        assert hasattr(g, "invoke")

    def test_compiles_with_in_memory_checkpointer(self):
        """build_graph(checkpointer=InMemorySaver()) compiles cleanly."""
        from langgraph.checkpoint.memory import InMemorySaver
        from agents.pipeline.graph import build_graph

        g = build_graph(checkpointer=InMemorySaver())
        assert hasattr(g, "invoke")

    def test_graph_has_expected_nodes(self):
        """All five expected node names are present in the compiled graph."""
        from agents.pipeline.graph import build_graph

        g = build_graph()
        # LangGraph exposes node names via graph.nodes
        node_names = set(g.nodes)
        for expected in ("ingest", "ner", "embed", "kg", "manifold"):
            assert expected in node_names, f"Missing node: {expected}"


# ---------------------------------------------------------------------------
# node_ingest
# ---------------------------------------------------------------------------

class TestNodeIngest:
    def test_successful_ingest_updates_state(self):
        from agents.pipeline.graph import node_ingest

        mock_result = MagicMock()
        mock_result.visible_text = "Visible content"
        mock_result.hidden_text = "Hidden content"
        mock_result.ocr_text = ""
        mock_result.has_hidden_text = True
        mock_result.file_hash = "abc123"
        mock_result.page_count = 3

        mock_agent = MagicMock()
        mock_agent.extract.return_value = mock_result

        with patch("agents.ingest_agent.IngestAgent", return_value=mock_agent):
            state = node_ingest(_base_state())

        assert state["file_hash"] == "abc123"
        assert state["visible_text"] == "Visible content"
        assert state["has_hidden_text"] is True
        assert state["page_count"] == 3
        assert "ingest" in state["completed_stages"]
        assert state["error"] is None

    def test_failed_ingest_sets_error(self):
        from agents.pipeline.graph import node_ingest

        mock_agent = MagicMock()
        mock_agent.extract.return_value = None

        with patch("agents.ingest_agent.IngestAgent", return_value=mock_agent):
            state = node_ingest(_base_state())

        assert state["error"] == "ingest failed"
        assert "ingest_failed" in state["completed_stages"]


# ---------------------------------------------------------------------------
# node_ner
# ---------------------------------------------------------------------------

class TestNodeNER:
    def test_ner_populates_entities(self):
        from agents.pipeline.graph import node_ner

        mock_entity = MagicMock()
        mock_entity.text = "Jane Doe"
        mock_entity.label = "PERSON"
        mock_entity.confidence = 0.99
        mock_entity.normalized = "jane doe"
        mock_entity.source = "spacy"

        mock_agent = MagicMock()
        mock_agent.extract.return_value = [mock_entity]

        with patch("agents.ner_agent.NERAgent", return_value=mock_agent):
            state = node_ner(_base_state(visible_text="Jane Doe works here."))

        assert state["entity_count"] == 1
        assert state["entities"][0]["normalized"] == "jane doe"
        assert "ner" in state["completed_stages"]

    def test_ner_empty_text_returns_empty_entities(self):
        from agents.pipeline.graph import node_ner

        mock_agent = MagicMock()
        mock_agent.extract.return_value = []

        with patch("agents.ner_agent.NERAgent", return_value=mock_agent):
            state = node_ner(_base_state())

        assert state["entity_count"] == 0
        assert state["entities"] == []


# ---------------------------------------------------------------------------
# node_embed
# ---------------------------------------------------------------------------

class TestNodeEmbed:
    def test_embed_produces_doc_and_entity_vectors(self):
        import numpy as np
        from agents.pipeline.graph import node_embed

        mock_agent = MagicMock()
        mock_agent.embed_single.return_value = MagicMock(
            tolist=lambda: [0.1] * 384
        )
        mock_agent.embed.return_value = [MagicMock(tolist=lambda: [0.2] * 384)]

        initial = _base_state(
            visible_text="Some text",
            entities=[
                {"normalized": "jane doe", "text": "Jane Doe",
                 "label": "PERSON", "confidence": 0.99, "source": "spacy"}
            ],
        )

        with patch("agents.embed_agent.EmbedAgent", return_value=mock_agent):
            state = node_embed(initial)

        assert state["doc_embedding"] is not None
        assert "jane doe" in state["entity_embeddings"]
        assert "embed" in state["completed_stages"]

    def test_embed_no_entities_skips_entity_embed(self):
        from agents.pipeline.graph import node_embed

        mock_agent = MagicMock()
        mock_agent.embed_single.return_value = MagicMock(
            tolist=lambda: [0.1] * 384
        )

        with patch("agents.embed_agent.EmbedAgent", return_value=mock_agent):
            state = node_embed(_base_state(visible_text="text", entities=[]))

        assert state["entity_embeddings"] == {}
        mock_agent.embed.assert_not_called()


# ---------------------------------------------------------------------------
# node_manifold
# ---------------------------------------------------------------------------

class TestNodeManifold:
    def test_manifold_skipped_when_too_few_entities(self):
        """Manifold is skipped when fewer than 5 entity vectors exist."""
        from agents.pipeline.graph import node_manifold

        state = node_manifold(
            _base_state(entity_embeddings={"a": [0.1] * 64, "b": [0.2] * 64})
        )
        assert state["n_clusters"] == 0
        assert "manifold_skipped" in state["completed_stages"]

    def test_manifold_runs_with_enough_entities(self):
        """With >=5 entities, ManifoldAgent is called and output stored."""
        import numpy as np
        from agents.pipeline.graph import node_manifold

        mock_agent = MagicMock()
        mock_agent.full_pipeline.return_value = {
            "labels": np.array([0, 1, 0, 1, 2]),
            "n_clusters": 3,
        }

        fake_vecs = {f"ent{i}": [float(i)] * 64 for i in range(5)}

        with patch("agents.manifold_agent.ManifoldAgent", return_value=mock_agent):
            state = node_manifold(_base_state(entity_embeddings=fake_vecs))

        assert state["n_clusters"] == 3
        assert state["cluster_labels"] == [0, 1, 0, 1, 2]
        assert "manifold" in state["completed_stages"]


# ---------------------------------------------------------------------------
# _should_stop routing
# ---------------------------------------------------------------------------

class TestShouldStop:
    def test_stop_when_error_present(self):
        from agents.pipeline.graph import _should_stop
        assert _should_stop({"error": "ingest failed"}) == "stop"

    def test_continue_when_no_error(self):
        from agents.pipeline.graph import _should_stop
        assert _should_stop({"error": None}) == "continue"

    def test_continue_when_error_key_missing(self):
        from agents.pipeline.graph import _should_stop
        assert _should_stop({}) == "continue"

"""
SPECTOR Test Configuration

Shared pytest fixtures for all test modules.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_doc():
    """A minimal document record fixture."""
    return {
        "doc_id": "testdoc0001",
        "source_url": "https://example.com/test.pdf",
        "raw_text": "Jeffrey Epstein met with Bill Gates on March 1 2011 at JPMorgan Chase offices.",
        "hidden_text": "",
        "pages": 1,
        "metadata": {},
    }


@pytest.fixture
def sample_entities():
    """Minimal entity records fixture."""
    return [
        {
            "entity_id": "ent001",
            "label": "PERSON",
            "text": "Jeffrey Epstein",
            "doc_id": "testdoc0001",
            "confidence": 0.98,
            "span_start": 0,
            "span_end": 15,
        },
        {
            "entity_id": "ent002",
            "label": "PERSON",
            "text": "Bill Gates",
            "doc_id": "testdoc0001",
            "confidence": 0.95,
            "span_start": 25,
            "span_end": 35,
        },
    ]


@pytest.fixture
def sample_embeddings():
    """Minimal embedding records fixture (low-dim for test speed)."""
    import random
    rng = random.Random(42)
    return [
        {
            "embed_id": "emb001",
            "source_id": "testdoc0001",
            "source_type": "document",
            "vector": [rng.gauss(0, 1) for _ in range(384)],
            "model": "all-MiniLM-L6-v2",
            "layer": "visible",
        },
        {
            "embed_id": "emb002",
            "source_id": "testdoc0001",
            "source_type": "document",
            "vector": [rng.gauss(0.1, 1) for _ in range(384)],  # slightly different
            "model": "all-MiniLM-L6-v2",
            "layer": "hidden",
        },
        {
            "embed_id": "emb003",
            "source_id": "ent001",
            "source_type": "entity",
            "vector": [rng.gauss(0, 1) for _ in range(384)],
            "model": "all-MiniLM-L6-v2",
            "layer": "visible",
        },
    ]


@pytest.fixture
def minimal_state(sample_doc, sample_entities, sample_embeddings):
    """Full minimal PipelineState for integration tests."""
    return {
        "source_urls": ["https://example.com/test.pdf"],
        "doc_dir": None,
        "use_tor": False,
        "gpu_tier": "cpu",
        "run_id": "test-run-001",
        "documents": [sample_doc],
        "entities": sample_entities,
        "embeddings": sample_embeddings,
        "media_probes": [],
        "errors": [],
        "kg_nodes_written": 0,
        "kg_edges_written": 0,
        "stage": "test",
        "complete": False,
    }

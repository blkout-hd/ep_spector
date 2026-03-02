"""Tests for EmbedAgent."""
import numpy as np


def test_embed_returns_correct_shape(embed_agent):
    texts = ["Hello world", "Second document", "Third piece of text"]
    result = embed_agent.embed(texts)
    assert result.shape[0] == 3
    assert result.ndim == 2


def test_embed_empty_returns_empty(embed_agent):
    result = embed_agent.embed([])
    assert result.shape[0] == 0


def test_embedding_delta_norm(embed_agent):
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    delta = embed_agent.embedding_delta_norm(v1, v2)
    assert abs(delta - np.sqrt(2)) < 1e-5


def test_normalized_embeddings_unit_length(embed_agent):
    vecs = embed_agent.embed(["test normalization"])
    norms = np.linalg.norm(vecs, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)

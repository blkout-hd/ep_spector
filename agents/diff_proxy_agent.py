"""
SPECTOR Diff Proxy Agent (Suppression Scorer)

Computes the suppression score for each document:

    score(doc) = ||embed(hidden_text) - embed(visible_text)||_2

A high score means the hidden text layer is semantically distant
from the visible text — indicating potentially significant redaction
or content buried in the PDF invisible text layer.

Results are stored per doc_id in state["suppression_scores"].
"""
from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger("spector.agents.diff_proxy")


def run(state: dict) -> dict:
    """
    Pipeline node: compute per-document suppression scores.

    Returns dict patch:
      - suppression_scores: dict[doc_id, float]
      - errors: list[str]
    """
    embeddings = state.get("embeddings", [])
    errors = []

    # Index by (source_id, layer)
    embed_index: dict[tuple, list[float]] = {}
    for emb in embeddings:
        if emb.get("source_type") == "document":
            key = (emb["source_id"], emb["layer"])
            embed_index[key] = emb["vector"]

    scores: dict[str, float] = {}
    doc_ids = {e["source_id"] for e in embeddings if e.get("source_type") == "document"}

    for doc_id in doc_ids:
        vis = embed_index.get((doc_id, "visible"))
        hid = embed_index.get((doc_id, "hidden"))
        if vis is None or hid is None:
            continue
        try:
            delta = np.array(hid) - np.array(vis)
            score = float(np.linalg.norm(delta))
            scores[doc_id] = score
            if score > 0.3:
                logger.info("High suppression score: doc=%s score=%.4f", doc_id, score)
        except Exception as exc:
            errors.append(f"diff_proxy:{doc_id}:{exc}")

    logger.info("Diff proxy complete: %d scored docs", len(scores))
    return {"suppression_scores": scores, "errors": errors}

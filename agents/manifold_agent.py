"""
SPECTOR Manifold Agent

Dimensionality reduction and clustering on entity/document embeddings.

Strategy:
  1. Collect all entity embeddings from state
  2. UMAP reduction to 15D (GPU via cuML if available, else scikit)
  3. HDBSCAN clustering on UMAP coords
  4. Store cluster assignments back to state for KG annotation
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger("spector.agents.manifold")


def _get_umap_reducer(n_components: int, gpu_tier: str):
    """Return cuML UMAP if GPU available, else umap-learn."""
    if gpu_tier in ("cuda12x", "cuda13x"):
        try:
            from cuml.manifold import UMAP as cuUMAP
            logger.info("Using cuML UMAP (GPU)")
            return cuUMAP(n_components=n_components, n_neighbors=15, min_dist=0.1)
        except ImportError:
            logger.warning("cuML not available, falling back to CPU UMAP")
    from umap import UMAP
    return UMAP(n_components=n_components, n_neighbors=15, min_dist=0.1, random_state=42)


def _get_hdbscan(gpu_tier: str):
    if gpu_tier in ("cuda12x", "cuda13x"):
        try:
            from cuml.cluster import HDBSCAN as cuHDBSCAN
            return cuHDBSCAN(min_cluster_size=3)
        except ImportError:
            pass
    from hdbscan import HDBSCAN
    return HDBSCAN(min_cluster_size=3, prediction_data=True)


def run(state: dict) -> dict:
    """
    Pipeline node: UMAP + HDBSCAN on entity embeddings.

    Returns dict patch:
      - umap_coords: list[list[float]]
      - clusters: list[int]
      - errors: list[str]
    """
    embeddings = state.get("embeddings", [])
    gpu_tier = state.get("gpu_tier", "cpu")
    errors = []

    entity_embeddings = [
        e for e in embeddings
        if e.get("source_type") == "entity" and e.get("layer") == "visible"
    ]

    if len(entity_embeddings) < 5:
        logger.warning("Too few entity embeddings (%d) for manifold", len(entity_embeddings))
        return {"umap_coords": [], "clusters": [], "errors": errors}

    try:
        matrix = np.array([e["vector"] for e in entity_embeddings], dtype=np.float32)
        n_components = min(15, matrix.shape[1] - 1, matrix.shape[0] - 1)

        reducer = _get_umap_reducer(n_components, gpu_tier)
        coords = reducer.fit_transform(matrix)

        clusterer = _get_hdbscan(gpu_tier)
        labels = clusterer.fit_predict(coords)

        logger.info("Manifold: %d points, %d clusters",
                    len(entity_embeddings), len(set(labels)) - (1 if -1 in labels else 0))

        return {
            "umap_coords": coords.tolist(),
            "clusters": labels.tolist(),
            "errors": errors,
        }
    except Exception as exc:
        logger.error("Manifold failed: %s", exc)
        return {"umap_coords": [], "clusters": [], "errors": [f"manifold:{exc}"]}

"""
SPECTOR Embed Agent

Encodes documents and entities to dense vector embeddings using
BGE-M3 (primary) or sentence-transformers all-MiniLM-L6-v2 (fallback).

Both visible and hidden text layers are encoded separately so the
diff_proxy_agent can compute suppression delta vectors.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any

logger = logging.getLogger("spector.agents.embed")

_PRIMARY_MODEL = "BAAI/bge-m3"
_FALLBACK_MODEL = "all-MiniLM-L6-v2"
_encoder = None


def _get_encoder():
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer
        try:
            _encoder = SentenceTransformer(_PRIMARY_MODEL)
            logger.info("Loaded encoder: %s", _PRIMARY_MODEL)
        except Exception:
            _encoder = SentenceTransformer(_FALLBACK_MODEL)
            logger.info("Loaded fallback encoder: %s", _FALLBACK_MODEL)
    return _encoder


def _encode_texts(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    encoder = _get_encoder()
    vecs = encoder.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return [v.tolist() for v in vecs]


def run(state: dict) -> dict:
    """
    Pipeline node: encode documents (visible + hidden) and entities.

    Returns dict patch:
      - embeddings: list[EmbeddingRecord]
      - errors: list[str]
    """
    docs = state.get("documents", [])
    entities = state.get("entities", [])
    embeddings = []
    errors = []

    # --- Document embeddings ---
    try:
        visible_texts = [d.get("raw_text", "")[:8192] for d in docs]
        hidden_texts = [d.get("hidden_text", "")[:8192] for d in docs]
        doc_ids = [d.get("doc_id", f"doc_{i}") for i, d in enumerate(docs)]

        if visible_texts:
            vis_vecs = _encode_texts(visible_texts)
            for doc_id, vec in zip(doc_ids, vis_vecs):
                embeddings.append({
                    "embed_id": hashlib.sha256(f"{doc_id}:visible".encode()).hexdigest()[:16],
                    "source_id": doc_id,
                    "source_type": "document",
                    "vector": vec,
                    "model": _PRIMARY_MODEL,
                    "layer": "visible",
                })

        non_empty_hidden = [(i, t) for i, t in enumerate(hidden_texts) if t.strip()]
        if non_empty_hidden:
            indices, htexts = zip(*non_empty_hidden)
            hid_vecs = _encode_texts(list(htexts))
            for idx, vec in zip(indices, hid_vecs):
                doc_id = doc_ids[idx]
                embeddings.append({
                    "embed_id": hashlib.sha256(f"{doc_id}:hidden".encode()).hexdigest()[:16],
                    "source_id": doc_id,
                    "source_type": "document",
                    "vector": vec,
                    "model": _PRIMARY_MODEL,
                    "layer": "hidden",
                })

    except Exception as exc:
        logger.error("Document embedding failed: %s", exc)
        errors.append(f"embed:docs:{exc}")

    # --- Entity embeddings ---
    try:
        if entities:
            ent_texts = [f"{e.get('label', '')}: {e.get('text', '')}"
                         for e in entities]
            ent_ids = [e.get("entity_id", f"ent_{i}") for i, e in enumerate(entities)]
            ent_vecs = _encode_texts(ent_texts)
            for ent_id, vec in zip(ent_ids, ent_vecs):
                embeddings.append({
                    "embed_id": hashlib.sha256(f"{ent_id}:entity".encode()).hexdigest()[:16],
                    "source_id": ent_id,
                    "source_type": "entity",
                    "vector": vec,
                    "model": _PRIMARY_MODEL,
                    "layer": "visible",
                })
    except Exception as exc:
        logger.error("Entity embedding failed: %s", exc)
        errors.append(f"embed:entities:{exc}")

    logger.info("Embed complete: %d vectors", len(embeddings))
    return {"embeddings": embeddings, "errors": errors}

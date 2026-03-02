"""
SPECTOR LangGraph StateGraph -- wires all agents into a pipeline.
"""
from __future__ import annotations

import logging
from typing import Optional

from langgraph.graph import StateGraph, END

from .state import PipelineState

logger = logging.getLogger(__name__)


def node_ingest(state: PipelineState) -> PipelineState:
    from agents.ingest_agent import IngestAgent

    agent = IngestAgent(ocr_enabled=True)
    result = agent.extract(state["source"])
    if result is None:
        return {**state, "error": "ingest failed", "completed_stages": ["ingest_failed"]}
    return {
        **state,
        "visible_text": result.visible_text,
        "hidden_text": result.hidden_text,
        "ocr_text": result.ocr_text,
        "has_hidden_text": result.has_hidden_text,
        "file_hash": result.file_hash,
        "page_count": result.page_count,
        "completed_stages": ["ingest"],
    }


def node_ner(state: PipelineState) -> PipelineState:
    from agents.ner_agent import NERAgent

    agent = NERAgent()
    entities = agent.extract(
        state.get("visible_text", "") + " " + state.get("hidden_text", "")
    )
    return {
        **state,
        "entities": [
            {
                "text": e.text,
                "label": e.label,
                "confidence": e.confidence,
                "normalized": e.normalized,
                "source": e.source,
            }
            for e in entities
        ],
        "entity_count": len(entities),
        "completed_stages": ["ner"],
    }


def node_embed(state: PipelineState) -> PipelineState:
    from agents.embed_agent import EmbedAgent

    agent = EmbedAgent()
    full_text = state.get("visible_text", "")[:8000]
    doc_vec = agent.embed_single(full_text)

    entity_texts = list({e["normalized"] for e in state.get("entities", [])})
    entity_vecs = {}
    if entity_texts:
        vecs = agent.embed(entity_texts)
        entity_vecs = {t: v.tolist() for t, v in zip(entity_texts, vecs)}

    return {
        **state,
        "doc_embedding": doc_vec.tolist(),
        "entity_embeddings": entity_vecs,
        "completed_stages": ["embed"],
    }


def node_kg(state: PipelineState) -> PipelineState:
    from agents.ner_agent import Entity
    from agents.kg_expand_agent import KGExpandAgent

    agent = KGExpandAgent()
    entities = [
        Entity(
            text=e["text"],
            label=e["label"],
            start=0,
            end=0,
            confidence=e["confidence"],
            source=e["source"],
            normalized=e["normalized"],
        )
        for e in state.get("entities", [])
    ]
    doc_id = state.get("file_hash", "unknown")
    id_map = agent.write_entities(entities, doc_id)
    edges = agent.write_cooccurrences(entities, doc_id)
    agent.close()
    return {
        **state,
        "kg_node_ids": id_map,
        "kg_edges_written": edges,
        "completed_stages": ["kg"],
    }


def node_manifold(state: PipelineState) -> PipelineState:
    import numpy as np
    from agents.manifold_agent import ManifoldAgent

    entity_vecs = state.get("entity_embeddings", {})
    if len(entity_vecs) < 5:
        return {**state, "n_clusters": 0, "completed_stages": ["manifold_skipped"]}

    agent = ManifoldAgent()
    mat = np.array(list(entity_vecs.values()), dtype=np.float32)
    result = agent.full_pipeline(mat)
    return {
        **state,
        "cluster_labels": result["labels"].tolist(),
        "n_clusters": result["n_clusters"],
        "completed_stages": ["manifold"],
    }


def _should_stop(state: PipelineState) -> str:
    return "stop" if state.get("error") else "continue"


def build_graph(checkpointer: Optional[object] = None) -> StateGraph:
    """Build and compile the LangGraph StateGraph.

    If a checkpointer is provided, compile the graph with persistence enabled.
    Otherwise, compile without persistence (stateless execution).
    """
    g = StateGraph(PipelineState)

    g.add_node("ingest", node_ingest)
    g.add_node("ner", node_ner)
    g.add_node("embed", node_embed)
    g.add_node("kg", node_kg)
    g.add_node("manifold", node_manifold)

    g.set_entry_point("ingest")
    g.add_conditional_edges("ingest", _should_stop, {"stop": END, "continue": "ner"})
    g.add_edge("ner", "embed")
    g.add_edge("embed", "kg")
    g.add_edge("kg", "manifold")
    g.add_edge("manifold", END)

    if checkpointer is not None:
        logger.info("Compiling graph with checkpointer %s", type(checkpointer).__name__)
        return g.compile(checkpointer=checkpointer)
    return g.compile()

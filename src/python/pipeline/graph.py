"""
SPECTOR LangGraph StateGraph definition.

Builds the full directed pipeline graph:
  ingest → ner → embed → media_probe → kg_write → manifold → diff_proxy → END

Parallel branches (ner + media_probe) fan out from ingest and
join at kg_write via Send API.
"""
from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import StateGraph, END
from langgraph.constants import Send

from .state import PipelineState

logger = logging.getLogger("spector.pipeline.graph")


def _import_agent(module: str, fn: str):
    """Lazy-import an agent function to avoid circular deps."""
    import importlib
    mod = importlib.import_module(f"agents.{module}")
    return getattr(mod, fn)


def ingest_node(state: PipelineState) -> dict[str, Any]:
    """Ingest documents from source_urls or doc_dir."""
    run = _import_agent("ingest_agent", "run")
    return run(state)


def ner_node(state: PipelineState) -> dict[str, Any]:
    """Run NER over ingested documents."""
    run = _import_agent("ner_agent", "run")
    return run(state)


def embed_node(state: PipelineState) -> dict[str, Any]:
    """Encode documents and entities to embedding vectors."""
    run = _import_agent("embed_agent", "run")
    return run(state)


def media_probe_node(state: PipelineState) -> dict[str, Any]:
    """Probe source URLs for related media files."""
    run = _import_agent("media_probe_agent", "run")
    return run(state)


def kg_write_node(state: PipelineState) -> dict[str, Any]:
    """Write entities and relationships to Neo4j KG."""
    run = _import_agent("kg_expand_agent", "run")
    return run(state)


def manifold_node(state: PipelineState) -> dict[str, Any]:
    """UMAP + HDBSCAN on entity embeddings."""
    run = _import_agent("manifold_agent", "run")
    return run(state)


def diff_proxy_node(state: PipelineState) -> dict[str, Any]:
    """Compute suppression scores: delta between visible and hidden embeddings."""
    run = _import_agent("diff_proxy_agent", "run")
    return run(state)


def route_after_ingest(state: PipelineState) -> list[Send]:
    """
    Fan-out router: after ingest, dispatch NER and media probe in parallel.
    Each document gets its own NER send; media probe runs once per URL batch.
    """
    sends = []
    for doc in state.get("documents", []):
        sends.append(Send("ner", {**state, "documents": [doc]}))
    if state.get("source_urls"):
        sends.append(Send("media_probe", state))
    return sends or [Send("embed", state)]


def build_graph() -> StateGraph:
    """
    Assemble and compile the full SPECTOR StateGraph.

    Returns:
        Compiled LangGraph graph ready for .invoke() or .stream()
    """
    g = StateGraph(PipelineState)

    g.add_node("ingest", ingest_node)
    g.add_node("ner", ner_node)
    g.add_node("embed", embed_node)
    g.add_node("media_probe", media_probe_node)
    g.add_node("kg_write", kg_write_node)
    g.add_node("manifold", manifold_node)
    g.add_node("diff_proxy", diff_proxy_node)

    g.set_entry_point("ingest")
    g.add_conditional_edges("ingest", route_after_ingest, ["ner", "media_probe", "embed"])
    g.add_edge("ner", "embed")
    g.add_edge("media_probe", "kg_write")
    g.add_edge("embed", "kg_write")
    g.add_edge("kg_write", "manifold")
    g.add_edge("manifold", "diff_proxy")
    g.add_edge("diff_proxy", END)

    return g.compile()

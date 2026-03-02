"""
LangGraph pipeline state definition.
Typed state that flows through all agent nodes.
"""
from __future__ import annotations
from typing import TypedDict, Optional, Annotated
import operator


class PipelineState(TypedDict):
    # Input
    source: str                          # URL or file path
    doc_id: Optional[str]                # Set after ingest

    # Extracted content
    visible_text: str
    hidden_text: str
    ocr_text: str
    has_hidden_text: bool
    file_hash: str
    page_count: int

    # NER results
    entities: list[dict]                 # serialized Entity objects
    entity_count: int

    # Embeddings
    doc_embedding: Optional[list[float]] # single doc-level embedding
    entity_embeddings: dict[str, list[float]]  # entity_text -> embedding

    # KG
    kg_node_ids: dict[str, str]          # entity_text -> neo4j id
    kg_edges_written: int

    # Manifold
    cluster_labels: Optional[list[int]]
    n_clusters: int

    # Control flow
    error: Optional[str]
    completed_stages: Annotated[list[str], operator.add]  # accumulates

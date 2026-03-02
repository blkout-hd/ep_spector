"""
Pipeline State definition for SPECTOR LangGraph graph.

All agent nodes read and write to this shared TypedDict,
enabling stateful multi-step document analysis.
"""
from __future__ import annotations

from typing import Annotated, Any, Optional
from typing_extensions import TypedDict
import operator


class DocumentRecord(TypedDict, total=False):
    """A single document flowing through the pipeline."""
    doc_id: str
    source_url: str
    raw_text: str
    hidden_text: str          # OCR-recovered or redaction-lifted text
    pages: int
    pdf_path: Optional[str]
    metadata: dict[str, Any]


class EntityRecord(TypedDict, total=False):
    """A named entity extracted from a document."""
    entity_id: str
    label: str                # PERSON, ORG, DATE, LOCATION, etc.
    text: str
    doc_id: str
    confidence: float
    span_start: int
    span_end: int


class EmbeddingRecord(TypedDict, total=False):
    """An embedding vector tied to a document or entity."""
    embed_id: str
    source_id: str            # doc_id or entity_id
    source_type: str          # 'document' | 'entity'
    vector: list[float]
    model: str
    layer: str                # 'visible' | 'hidden' | 'delta'


class MediaProbeResult(TypedDict, total=False):
    """Result from probing for related media files."""
    base_url: str
    found_urls: list[str]
    status_codes: dict[str, int]
    via_tor: bool


class PipelineState(TypedDict, total=False):
    """
    Shared state flowing through all SPECTOR pipeline nodes.

    Uses Annotated[list, operator.add] for append-only accumulation
    across parallel branches; plain fields are last-write-wins.
    """
    # --- Input configuration ---
    source_urls: list[str]
    doc_dir: Optional[str]
    use_tor: bool
    gpu_tier: str             # 'cpu' | 'cuda12x' | 'cuda13x'
    run_id: str

    # --- Accumulated results (append-only via reducer) ---
    documents: Annotated[list[DocumentRecord], operator.add]
    entities: Annotated[list[EntityRecord], operator.add]
    embeddings: Annotated[list[EmbeddingRecord], operator.add]
    media_probes: Annotated[list[MediaProbeResult], operator.add]
    errors: Annotated[list[str], operator.add]

    # --- KG write status ---
    kg_nodes_written: int
    kg_edges_written: int

    # --- Manifold output ---
    umap_coords: Optional[list[list[float]]]
    clusters: Optional[list[int]]

    # --- Suppression scoring ---
    suppression_scores: Optional[dict[str, float]]  # doc_id -> score

    # --- Pipeline control ---
    stage: str               # current stage name for routing
    complete: bool

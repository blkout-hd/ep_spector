# SPECTOR Agent Definitions

This file describes the Python agents that make up the processing pipeline.
It is **not** a system prompt and contains no operational secrets.

## IngestAgent

- **Module**: `agents/ingest_agent.py`
- **Input**: local path or URL to a PDF.
- **Output**: `ExtractedDocument` (visible text, hidden text, OCR text).
- **Notes**:
  - Uses PyMuPDF to extract text, including text under annotation rectangles.
  - Uses PaddleOCR for pages with no selectable text.
  - Does not bypass cryptographic protections.

## NERAgent

- **Module**: `agents/ner_agent.py`
- **Input**: raw text (visible + hidden).
- **Output**: list of `Entity` dataclasses.
- **Implementation**:
  - spaCy model for high-precision base NER.
  - Optional GLiNER model for zero-shot categories.
  - Deduplicates entities and normalizes names.

## EmbedAgent

- **Module**: `agents/embed_agent.py`
- **Responsibilities**:
  - Encode documents and entities into dense vectors.
  - Compute L2 delta norms between embeddings for suppression scoring.
  - Normalize embeddings to unit length for stable similarity.

## KGExpandAgent

- **Module**: `agents/kg_expand_agent.py`
- **Responsibilities**:
  - Write entities and relationships into Neo4j.
  - Support batch upserts and BFS-style graph expansion.

## ManifoldAgent

- **Module**: `agents/manifold_agent.py`
- **Responsibilities**:
  - Dimensionality reduction via UMAP.
  - Clustering via HDBSCAN.
  - Use GPU (cuML) when available, CPU otherwise.

## MediaProbeAgent

- **Module**: `agents/media_probe_agent.py`
- **Responsibilities**:
  - Probe for related media files by extension cycling.
  - Use aiohttp and optional Tor proxy for network access.

## DiffProxyAgent

- **Module**: `agents/diff_proxy_agent.py`
- **Responsibilities**:
  - Compare document versions via embedding deltas.
  - Produce suppression scores used in redaction/suppression analysis.

## Pipeline Orchestration

- **Module**: `agents/pipeline/graph.py`
- **State**: `PipelineState` in `agents/pipeline/state.py`.
- **Checkpointer**: configured in `agents/pipeline/checkpointer.py`.
- **Worker**: `agents/runner.py` executes the graph against Redis jobs.

# SPECTOR Architecture

## Overview

SPECTOR is a multi-layer system for analyzing publicly available documents,
extracting entities, and building a knowledge graph for downstream search
and investigation.

```text
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  Django REST API │ Admin Console (Tornado) │ Onion Service  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                        │
│               LangGraph StateGraph pipeline                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                         │
│  Python agents (ingest, NER, embed, KG, manifold, media)    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                          │
│  PostgreSQL │ Neo4j │ Qdrant │ Redis │ MongoDB │ DuckDB     │
└─────────────────────────────────────────────────────────────┘
```

## Layers

### Presentation

- **Django** (`src/python/spector_django/`): REST API for documents, entities,
  and privacy/erasure requests.
- **Tornado Admin Console**: Operational dashboard and (optionally) Tor
  onion service for secure access.

### Orchestration

- **LangGraph** pipeline (`agents/pipeline/`):
  - `state.py`: typed `PipelineState`.
  - `graph.py`: wires ingest → NER → embed → KG → manifold.
  - `checkpointer.py`: configures in-memory or SQLite persistence.
  - `agents/runner.py`: Redis-backed worker executing the graph.

### Processing

- **Ingest**: PyMuPDF + PaddleOCR for text and hidden layer extraction.
- **NER**: spaCy + GLiNER for person/organization/location entities.
- **Embedding**: BGE-M3 / sentence-transformers dense vectors.
- **Manifold**: UMAP + HDBSCAN for clustering in embedding space.
- **KG Expansion**: Neo4j-backed entity and relationship writes.
- **Media Probe**: Asynchronous discovery of related media via extension cycling.

### Storage

- **PostgreSQL**: Primary relational store (Django).
- **Neo4j**: Knowledge graph storage.
- **Qdrant / Chroma**: Vector search.
- **Redis**: Job queue + LangGraph checkpointing (optionally).
- **DuckDB / MongoDB**: Analytical and document collections.

## Data Flow (Happy Path)

1. Client submits a document URL or upload to `/api/documents/ingest/`.
2. Django persists a `Document` row and enqueues a job in Redis.
3. Worker pulls from `spector:ingest_queue` and runs the LangGraph pipeline.
4. Agents extract text, entities, embeddings, KG edges, and clusters.
5. Results are written to Neo4j/Qdrant and summarized back into Redis
   (`spector:result:<file_hash>`).
6. Clients query Django or MCP servers for search, KG queries, or media probes.

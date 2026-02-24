# SPECTOR Architecture

## System Overview

SPECTOR (Semantic Pipeline for Entity Correlation and Topological Organization Research) is a comprehensive document analysis and knowledge graph system designed for processing publicly available documents and building semantic relationships.

**⚠️ Legal Framework:** See [DISCLAIMER.md](DISCLAIMER.md) for legal compliance requirements and usage restrictions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────┤
│  Web UI (Django + D3.js)  │  API (REST/WebSocket)  │  Onion Service    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                              │
├─────────────────────────────────────────────────────────────────────────┤
│                    LangGraph StateGraph (Agent Orchestration)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ NER      │ │ Media    │ │ KG       │ │ Embed    │ │ Diff     │      │
│  │ Agent    │ │ Probe    │ │ Expand   │ │ UMAP     │ │ Proxy    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          PROCESSING LAYER                                │
├─────────────────────────────────────────────────────────────────────────┤
│  Python Services                    │  Julia Services                   │
│  ├─ PyMuPDF (hidden text)           │  ├─ PlasmoData.jl (DataGraph)    │
│  ├─ PaddleOCR (OCR)                 │  ├─ HyperGraphs.jl (n-ary)       │
│  ├─ spaCy/GLiNER (NER)              │  ├─ LightGraphs.jl (BFS)         │
│  ├─ cuDF (GPU DataFrame)            │  └─ UMAP.jl (dimensionality)     │
│  └─ cuML (UMAP, t-SNE, HDBSCAN)     │                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           STORAGE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Vector Stores        │  Graph Stores       │  Document Stores         │
│  ├─ Qdrant            │  ├─ Neo4j AuraDB    │  ├─ MongoDB (metadata)   │
│  ├─ Weaviate          │  ├─ LightRAG        │  ├─ DuckDB (analytics)   │
│  ├─ ChromaDB          │  └─ AuroraDB        │  └─ TileDB (arrays)      │
│  └─ Redis (cache)     │                     │  └─ AIStore (objects)    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Document Ingestion Pipeline

#### PDF Processing
```
PDF Input → PyMuPDF → [Visible Text Layer] [Hidden Text Layer] [OCR Overlay]
                     ↓                    ↓                    ↓
                extract_text()      get_bboxlog()      paddle_ocr()
                     ↓                    ↓                    ↓
                └────────────────────┬───────────────────────┘
                                     ↓
                              Normalized Text
```

#### Hidden Text Detection
- `page.get_bboxlog()` detects "ignore-text" items
- Tesseract OCR documents identified via GlyphLessFont
- Redacted text extraction via text stream analysis
- Suppression score calculation via embedding delta

### 2. Entity Extraction Pipeline

```
Normalized Text
       ↓
┌─────────────────┐
│ spaCy Pipeline  │ → Tokenization → POS Tagging → Dependency Parsing
└─────────────────┘
       ↓
┌─────────────────┐
│ NER Models      │ → PERSON | ORGANIZATION | LOCATION | DATE | EVENT
└─────────────────┘
       ↓
┌─────────────────┐
│ GLiNER Zero-shot│ → Custom entity types via prompting
└─────────────────┘
       ↓
Entity Candidates → Confidence Scoring → Deduplication → KG Insert
```

### 3. Embedding & Clustering Pipeline

```
Text Chunks
    ↓
┌─────────────────────────┐
│ BGE-M3 Encoder (cuDF)   │ → 768-dim dense vectors
│ - Dense embeddings       │
│ - Sparse embeddings      │
│ - BM25 lexical           │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ cuML UMAP (Parallel)    │ → 15-dim for clustering
│ - kNN graph (GPU)        │ → 2-dim for visualization
│ - SGD optimization       │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ cuML t-SNE (Parallel)   │ → 2-dim for viz
│ - Barnes-Hut (GPU)       │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ HDBSCAN Clustering      │ → Cluster labels
│ - Density-based          │
│ - Noise handling         │
└─────────────────────────┘
    ↓
Cluster Membership → KG Meta-Edges
```

### 4. Knowledge Graph Construction

```
Entities + Relationships
         ↓
┌─────────────────────────────────┐
│ Julia HyperGraphs.jl            │
│ - n-ary relationships           │
│ - [Person A] → [Location] →     │
│   [Person B] + [Date]           │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Recursive BFS Expansion         │
│ - Seed from entity CSVs         │
│ - Extract co-occurring entities │
│ - Add to frontier → Repeat      │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Neo4j Write (Batch Cypher)      │
│ - MERGE entities                │
│ - CREATE relationships          │
│ - SET cluster membership        │
└─────────────────────────────────┘
```

### 5. Media Discovery Pipeline

```
Document Base URLs (e.g., DOJ_EP_000012345.pdf)
         ↓
┌─────────────────────────────────┐
│ Extension Cycling (aiohttp+Tor) │
│ Extensions:                     │
│ - Video: .mp4, .avi, .mov, .mkv │
│ - Image: .jpg, .png             │
│ - Doc: .docx, .msg, .eml        │
│ - Archive: .zip                 │
└─────────────────────────────────┘
         ↓
HTTP Response Analysis
- 200: Available for download
- 403: Exists but access-controlled
- 404: Not found
         ↓
┌─────────────────────────────────┐
│ AIStore Ingestion               │
│ - GPUDirect storage             │
│ - S3-compatible API             │
│ - RDMA transfer                 │
└─────────────────────────────────┘
```

### 6. Negative Proxy Diffing

```
Redacted Document        Unredacted/Recovered
         ↓                        ↓
    e_redacted              e_recovered
    (visible OCR)           (hidden layer)
         ↓                        ↓
         └──────────┬─────────────┘
                    ↓
         delta = e_recovered - e_redacted
                    ↓
    suppression_score = ||delta||₂
                    ↓
    Sort by suppression_score DESC
    → Priority queue of heavily redacted docs
```

### 7. LangGraph Agent Orchestration

```python
class PipelineState(TypedDict):
    frontier: list[str]       # Entity expansion queue
    visited: set[str]         # Dedup set
    kg_edges: list[tuple]     # Neo4j write queue
    media_candidates: list    # Extension cycling queue
    embeddings: dict          # Document embeddings
    clusters: dict            # Cluster assignments

builder = StateGraph(PipelineState)

# Agent Nodes
builder.add_node("ner_extract", ner_agent)        # cuDF + spaCy
builder.add_node("kg_expand", julia_bfs_agent)    # Julia subprocess
builder.add_node("media_probe", probe_agent)      # aiohttp + Tor
builder.add_node("embed_umap", manifold_agent)    # cuML UMAP
builder.add_node("diff_proxy", delta_agent)       # Suppression scoring
builder.add_node("neo4j_write", graph_writer)     # Batch Cypher

# Edges (conditional routing)
builder.add_conditional_edges(
    "ner_extract",
    route_by_entity_type,
    {
        "person": "kg_expand",
        "org": "kg_expand",
        "location": "kg_expand",
        "unknown": "embed_umap"
    }
)

# Checkpointing
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
```

## Deployment Architecture

### Local Development
```
WSL2 Ubuntu
    ↓
Docker Compose
    ↓
┌─────────────────────────────────────┐
│ Containers:                         │
│ - qdrant:6333                       │
│ - neo4j:7687, 7474                  │
│ - redis:6379                        │
│ - mongodb:27017                     │
│ - django:8000                       │
│ - tornado:8888                      │
└─────────────────────────────────────┘
```

### Cloud Deployment (GCP Cloud Run)
```
Cloud Run Container
    ↓
┌─────────────────────────────────────┐
│ Serverless Services:                │
│ - Cloud SQL (PostgreSQL)            │
│ - Memorystore (Redis)               │
│ - Vertex AI (embeddings)            │
│ - Cloud Storage (AIStore equiv.)    │
└─────────────────────────────────────┘
```

### Onion Service Deployment
```
Tornado Web Server
    ↓
Tor Hidden Service
    ↓
.onion Address (anonymous access)
    ↓
┌─────────────────────────────────────┐
│ Security:                           │
│ - End-to-end encryption             │
│ - No IP logging                     │
│ - Circuit rotation                  │
│ - Rate limiting                     │
└─────────────────────────────────────┘
```

## Data Flow

### Ingestion Flow
1. Document sourced from public URL
2. Downloaded to AIStore
3. PDF processed (visible + hidden text)
4. OCR applied if needed
5. Text normalized and chunked
6. Entities extracted
7. Embeddings generated
8. Stored in vector + graph DBs

### Query Flow
1. User submits query via Web UI/API
2. Query embedded (same model as docs)
3. Vector similarity search (top-k)
4. Graph traversal from results
5. Reranking with cross-encoder
6. LLM synthesis (if enabled)
7. Results returned with citations

### Expansion Flow
1. Seed entities loaded from CSV
2. NER extracts co-occurring entities
3. New entities added to frontier
4. BFS expansion continues
5. Convergence or depth limit reached
6. KG updated with new relationships

## Security Considerations

### Data Protection
- All data encrypted at rest (AES-256)
- TLS 1.3 for all network communication
- Redis AUTH + ACLs enabled
- Neo4j authentication required
- MongoDB role-based access

### Access Control
- Django RBAC for web interface
- API key authentication for REST
- JWT tokens for WebSocket
- Rate limiting per IP/user
- Audit logging for all queries

### Privacy Compliance
- JSON-RPC 2.0 opt-out endpoint
- Data subject deletion workflow
- Audit trail for compliance
- Data retention policies
- PII anonymization options

## Performance Characteristics

### Benchmarks (Expected)
| Operation | CPU | GPU (CUDA) | Speedup |
|-----------|-----|------------|---------|
| BGE-M3 Embedding | 100 doc/s | 2000 doc/s | 20x |
| UMAP (100k docs) | 300s | 15s | 20x |
| t-SNE (100k docs) | 600s | 30s | 20x |
| HDBSCAN | 60s | 5s | 12x |
| NER (spaCy) | 500 doc/s | 5000 doc/s | 10x |

### Scaling
- Horizontal: Add more worker containers
- Vertical: GPU acceleration for embeddings
- Distributed: AIStore for object storage
- Caching: Redis LangCache for LLM responses

---

**Architecture Version:** 1.0.0  
**Last Updated:** 2026-02-19  
**Status:** Reference Implementation

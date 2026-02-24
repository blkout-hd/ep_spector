# SPECTOR

**Semantic Pipeline for Entity Correlation and Topological Organization Research**

> ⚠️ **IMPORTANT GOVERNMENT USE NOTICE**: This tool is designed exclusively for lawful analysis of publicly available government documents. Users must comply with all applicable laws, regulations, and guidelines governing use of disclosed materials. The legal framework for appropriate use of certain government-disclosed documents may not be entirely clear in all circumstances—users are responsible for exercising independent judgment to ensure compliance. **Do not use this tool for any prohibited purpose or outside applicable disclosure guidelines.** When in doubt, consult the originating agency's guidelines or legal counsel.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Julia 1.9+](https://img.shields.io/badge/julia-1.9+-purple.svg)](https://julialang.org/downloads/)

A comprehensive open-source document analysis and knowledge graph system for processing publicly available documents and building semantic relationships.

## ⚠️ Legal Notice

**This system is designed for processing publicly available documents only.**

Before using SPECTOR, please read the [DISCLAIMER.md](DISCLAIMER.md) for important legal information, usage restrictions, and compliance requirements.

### Legal Framework & Citations

This project respects and adheres to guidelines established by government agencies regarding disclosure and use of public documents. For matters related to specific investigations or disclosed materials, users should consult the relevant agency guidelines:

- **DOJ Epstein Investigation Materials**: [justice.gov/epstein](https://www.justice.gov/epstein) - Official framework governing use of publicly disclosed documents
- **FOIA Guidelines**: [foia.gov](https://www.foia.gov/) - Freedom of Information Act requests and guidelines
- **PACER**: [pacer.gov](https://pacer.gov/) - Public Access to Court Electronic Records

## Features

### Document Processing
- **PDF Hidden Text Extraction**: Detect and extract text hidden behind redaction boxes
- **OCR Integration**: PaddleOCR and Tesseract support for scanned documents
- **Multi-format Support**: PDF, DOCX, images, video, audio
- **GPU Acceleration**: CUDA-accelerated processing via RAPIDS

### Entity Extraction
- **NER Pipeline**: spaCy and GLiNER for named entity recognition
- **Custom Entities**: Zero-shot entity extraction via prompting
- **Entity Resolution**: Deduplication and normalization

### Vector Operations
- **BGE-M3 Embeddings**: Dense + sparse + lexical retrieval
- **UMAP Dimensionality Reduction**: GPU-accelerated manifold learning
- **t-SNE Visualization**: 2D/3D projections for exploration
- **HDBSCAN Clustering**: Density-based cluster discovery

### Knowledge Graph
- **Neo4j Integration**: Production-ready graph database
- **LightRAG**: Local Graph RAG with dual-level retrieval
- **N-ary Relationships**: HyperGraphs.jl for complex relationships
- **Recursive Expansion**: Julia-based BFS frontier expansion

### Media Discovery
- **Extension Cycling**: Automatic discovery of related media files
- **Tor Integration**: Anonymous probing via Tor network
- **AIStore**: Distributed object storage for large corpora

### AI Orchestration
- **LangGraph**: Stateful agent workflows
- **Redis LangCache**: Semantic caching for LLM responses
- **MCP Servers**: Model Context Protocol integration
- **Smithery Skills**: Extensible skill system

### Admin Console
- **Tornado Web Interface**: Real-time monitoring dashboard
- **Job Queue Management**: Monitor and manage processing jobs
- **System Health Metrics**: CPU, memory, and uptime tracking
- **WebSocket Updates**: Live metrics streaming
- **Configuration UI**: Manage system settings
- **RESTful API**: Programmatic access to admin functions

## Quick Start

### Prerequisites
- Python 3.10+
- Julia 1.9+ (optional, for graph expansion)
- Docker + Docker Compose
- NVIDIA GPU with CUDA 12.x/13.x (optional, for GPU acceleration)

### Installation

```bash
# Clone the repository
git clone https://github.com/SPECTOR/spector.git
cd spector

# Install Python dependencies
pip install -e .

# Install Julia dependencies (optional)
julia --project -e 'using Pkg; Pkg.instantiate()'

# Start services with Docker
docker compose up -d

# Run the system check
python -m spector

# Start admin console
python launcher.py admin --port 8888 --host localhost
```

### Admin Console Usage

The Tornado-based admin console provides a web interface for monitoring and managing SPECTOR:

```bash
# Start admin console (default: http://localhost:8888)
python launcher.py admin

# Custom port and host
python launcher.py admin --port 9000 --host 0.0.0.0

# Default credentials
# Username: admin
# Password: spector
```

**Admin Console Features:**
- **Dashboard**: Real-time system health metrics (CPU, memory, uptime)
- **Job Queue**: Monitor active document processing jobs
- **API Endpoints**: 
  - `GET /api/health` - System health status
  - `GET /api/jobs` - Job queue status
  - `GET /api/config` - System configuration
  - `GET /api/metrics` - Performance metrics
- **WebSocket**: `ws://localhost:8888/ws/metrics` - Live updates
- **Authentication**: Basic auth with configurable credentials

### Basic Usage

```python
from spector import SpectorPipeline

# Initialize pipeline
pipeline = SpectorPipeline(
    vector_store="qdrant",
    graph_db="neo4j",
    use_gpu=True
)

# Process documents
pipeline.ingest(["document1.pdf", "document2.pdf"])

# Extract entities
entities = pipeline.extract_entities()

# Build knowledge graph
pipeline.build_graph(entities)

# Query
results = pipeline.search("find all associations between X and Y")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  Web UI (Django) │ API (REST/WS) │ Onion Service (Tor)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                         │
│            LangGraph StateGraph (Agent Orchestration)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Processing Layer                           │
│  Python (PyMuPDF, spaCy, cuML) │ Julia (Graphs, UMAP)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                            │
│  Qdrant │ Neo4j │ Redis │ MongoDB │ DuckDB │ AIStore        │
└─────────────────────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Documentation

| Document | Description |
|----------|-------------|
| [DISCLAIMER.md](DISCLAIMER.md) | Legal framework and usage restrictions |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and design |
| [TODO.md](TODO.md) | Current tasks and roadmap |
| [AGENTS.md](AGENTS.md) | AI agent system prompt |
| [docs/KG_SCHEMA.md](docs/KG_SCHEMA.md) | Knowledge graph schema |

## Project Structure

```
SPECTOR/
├── AGENTS.md              # AI agent system prompt
├── ARCHITECTURE.md        # System architecture
├── DISCLAIMER.md          # Legal framework
├── TODO.md                # Task queue
├── memory.json            # Project memory
├── pyproject.toml         # Python dependencies
├── Project.toml           # Julia dependencies
├── docker-compose.yml     # Docker configuration
├── src/
│   ├── python/            # Python source code
│   │   └── spector.py
│   └── julia/             # Julia source code
│       └── SPECTOR.jl
├── agents/                # LangGraph agent definitions
├── mcp_servers/           # MCP server implementations
├── config/                # Configuration files
├── data/                  # Data directory (gitignored)
├── docs/                  # Documentation
└── tests/                 # Test suite
```

## Capabilities

### System Detection

SPECTOR automatically detects system capabilities and adapts:

```
╔═══════════════════════════════════════════════════════════════╗
║                    SPECTOR v1.0.0                             ║
╠═══════════════════════════════════════════════════════════════╣
║  System Capabilities:                                          ║
║    Python: 3.11.5 (main, Sep 2023)                             ║
║    CUDA:   cuda13x                                             ║
║    cuDF:   True                                                ║
║    Julia:  True                                                ║
╚═══════════════════════════════════════════════════════════════╝
```

### Adaptive Library Loading

```python
# Walrus-gated capability detection
cuda_tier = (
    "cuda13x" if (has_cupy := probe("cupy_cuda13x")) else
    "cuda12x" if probe("cupy_cuda12x") else
    "cuda_toolkit" if probe("cupy") else
    "cpu"
)
```

## Deployment

### Local Development
```bash
docker compose up -d
```

### GCP Cloud Run
```bash
gcloud run deploy spector \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Railway
```bash
railway up  # Reads docker-compose.yml
```

## Contributing

1. Read [DISCLAIMER.md](DISCLAIMER.md) for legal requirements
2. Review [TODO.md](TODO.md) for current tasks
3. Follow the code style (black + ruff)
4. Add tests for new features
5. Submit a pull request

## License

- **Core Framework**: MIT License
- **Graph Components**: AGPL-3.0
- **Documentation**: CC BY-SA 4.0

See [LICENSE](LICENSE) for full license text.

## Acknowledgments

This project builds upon the work of:
- [epstein-files.org](https://epstein-files.org) (Sifter Labs)
- [epstein-docs.github.io](https://epstein-docs.github.io) (Epstein Archive)
- [github.com/ErikVeland/epstein-archive](https://github.com/ErikVeland/epstein-archive)
- [Librarius](https://boltzmannentropy.github.io/Librarius/)
- [goyfiles.com](https://www.goyfiles.com)

### Open Source Dependencies

SPECTOR relies on the following open-source projects:

**Core Infrastructure:**
- [tornadoweb/tornado](https://github.com/tornadoweb/tornado) - Asynchronous web framework
- [pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) - Git hook framework
- [psf/black](https://github.com/psf/black) - Python code formatter
- [charliermarsh/ruff](https://github.com/charliermarsh/ruff) - Extremely fast Python linter

**Security & Secrets Management:**
- [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) - Secret scanning
- [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) - Secret detection
- [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) - Prevent secret commits

**Document Processing:**
- [pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF text extraction
- [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR engine
- [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) - OCR engine

**AI/ML:**
- [explosion/spaCy](https://github.com/explosion/spacy) - Named entity recognition
- [urchade/GLiNER](https://github.com/urchade/GLiNER) - Zero-shot NER
- [FlagOpen/FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) - BGE-M3 embeddings
- [rapidsai/cuml](https://github.com/rapidsai/cuml) - GPU-accelerated ML

**Graph & Vector Databases:**
- [neo4j/neo4j](https://github.com/neo4j/neo4j) - Graph database
- [qdrant/qdrant](https://github.com/qdrant/qdrant) - Vector database
- [chroma-core/chroma](https://github.com/chroma-core/chroma) - Vector database

**Agent Orchestration:**
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) - Stateful agent workflows

See respective repositories for licensing terms.

## Disclaimer

**This software is provided for academic research and educational purposes only.**

Users are responsible for ensuring compliance with all applicable laws and regulations. The authors and contributors disclaim all liability for any misuse of this software.

See [DISCLAIMER.md](DISCLAIMER.md) for full legal framework.

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-19  
**Status:** Active Development

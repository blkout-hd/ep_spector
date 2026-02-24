# SPECTOR

**S**emantic **P**ipeline for **E**ntity **C**orrelation and **T**opological **O**rganization **R**esearch

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

> **Legal & Ethical Use**
>
> SPECTOR is designed to analyze **publicly released** documents (e.g., DOJ public libraries, FOIA releases, open-source archives).  
> It does **not** attempt to access sealed records, paywalled content in violation of terms, or non-public systems.  
> If a dataset is not lawfully and publicly accessible, do not point SPECTOR at it.

---

## 🎯 Overview

SPECTOR is an **open-source research toolkit** for building knowledge graphs from public document archives. It combines:

- **Advanced NLP** (spaCy, GLiNER) for entity extraction
- **Vector search** (Qdrant, Weaviate) with BGE-M3 embeddings
- **Graph databases** (Neo4j) for relationship mapping  
- **GPU acceleration** (cuML, cuDF) for large-scale analysis
- **Agent orchestration** (LangGraph) for automated workflows

Originally developed to analyze public court documents and FOIA releases, SPECTOR helps researchers discover hidden connections and patterns in large document collections.

---

## ✨ Key Features

- 📄 **Multi-format Document Processing**: PDF (PyMuPDF), OCR (PaddleOCR), HTML, plaintext
- 🧠 **Named Entity Recognition**: Extract persons, organizations, locations, dates, events
- 🔗 **Knowledge Graph Construction**: Automatic relationship inference with Neo4j
- 🔍 **Semantic Search**: 768-dimensional BGE-M3 embeddings with UMAP clustering
- ⚡ **GPU Acceleration**: 10-15x speedup with CUDA-optimized pipeline
- 🤖 **AI Agent Workflows**: LangGraph state machines for complex analysis
- 🔒 **Privacy-First**: Local-only processing, no external data transmission
- 🛡️ **Security Hardened**: Pre-commit hooks, secret detection, PII scanning

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (3.11 recommended)
- **Docker & Docker Compose** (for databases)
- **(Optional) CUDA 12.x/13.x** for GPU acceleration

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/SPECTOR.git
cd SPECTOR

# Install dependencies
pip install -e ".[dev]"

# (Optional) Install GPU support
pip install -e ".[cuda-12x]"  # Or cuda-13x

# Start infrastructure
docker compose up -d

# Install pre-commit hooks
pre-commit install

# Run the CLI
spector --help
```

### Basic Usage

```bash
# Index a directory of PDFs
spector index ./documents --output-graph ./output.db

# Search for entities
spector search "John Doe" --graph ./output.db

# Export knowledge graph
spector export ./output.db --format graphml

# Launch interactive UI
spector ui --graph ./output.db --port 8000
```

---

## 📁 Architecture

```
SPECTOR/
├── src/
│   ├── python/spector/
│   │   ├── cli.py              # Command-line interface
│   │   ├── pipeline/           # Document processing pipeline
│   │   ├── agents/             # LangGraph agent workflows
│   │   ├── kg/                 # Knowledge graph operations
│   │   └── embeddings/         # Vector search & UMAP
│   └── julia/                  # (Future) Julia components
├── docker-compose.yml          # Neo4j, Qdrant, Redis, MongoDB
├── pyproject.toml              # Python dependencies & config
├── .pre-commit-config.yaml     # Security & code quality hooks
└── README.md                   # This file
```

### Data Flow

```
PDF/HTML → OCR → NER → Entity Extraction → Knowledge Graph
                                        ↓
                        Vector Embeddings → UMAP Clustering
```

---

## 🗄️ Data Sources

You are expected to configure your own data sources. Typical examples include:

- **Public DOJ or court document libraries** that are intentionally released for public access
- **Public open-source archives** (e.g., epstein-files.org, epstein-docs.github.io, Librarius, ErikVeland/epstein-archive)
- **FOIA libraries** and government public records
- **Other open datasets** and document collections you are legally entitled to process

**SPECTOR does not ship with any proprietary datasets or facilitate access to non-public systems.**

---

## 🛠️ Configuration

### Environment Variables

Create `.env` from `.env.example`:

```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key

# Redis (LangCache)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=spector

# AI Providers (optional - for agent orchestration)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### Docker Services

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f neo4j
```

---

## 🤖 CLI Launcher with AI Provider Selection

SPECTOR includes an intelligent CLI launcher that can automatically configure AI providers for agent orchestration:

```bash
# Interactive setup
python launcher.py

# Or specify provider directly
spector --ai-provider gemini-cli index ./documents
spector --ai-provider qwen-cli search "pattern"
spector --ai-provider claude-code analyze ./graph.db
```

Supported AI providers:
- **Gemini CLI** (Google - free tier available)
- **Qwen CLI** (Alibaba - open source)
- **Claude Code** (Anthropic)
- **GitHub Copilot CLI**
- **GPT Codex** (OpenAI)
- **Local models** via Ollama/LM Studio

---

## 🧪 Development

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=spector --cov-report=html
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type checking
mypy src/

# Security scan
bandit -r src/

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## 🌐 Cross-Platform Support

SPECTOR supports multiple platforms and architectures:

- **Operating Systems**: Windows, Linux, macOS
- **Architectures**: x86_64, ARM64 (Apple Silicon, AWS Graviton)
- **Python**: 3.10, 3.11, 3.12
- **GPUs**: NVIDIA CUDA 12.x/13.x (optional)

Build configurations are managed via `pyproject.toml` with platform-specific optional dependencies.

---

## 📚 Documentation

- **[Architecture](ARCHITECTURE.md)**: System design and components
- **[Disclaimer](DISCLAIMER_OSS.md)**: Legal notice and usage guidelines
- **[Security](SECURITY.md)**: Vulnerability reporting policy
- **[Contributing](CONTRIBUTING.md)**: How to contribute
- **[Changelog](CHANGELOG.md)**: Version history

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters (`pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

SPECTOR is released under the **MIT License**. See [LICENSE](./LICENSE) for details.

**Copyright © 2024-2026 SPECTOR Contributors**

---

## 🙏 Acknowledgments

SPECTOR builds on excellent open-source projects:

- **LangChain** & **LangGraph** - Agent orchestration
- **Neo4j** - Graph database
- **Qdrant** - Vector search
- **spaCy** & **GLiNER** - NLP and NER
- **RAPIDS cuML/cuDF** - GPU acceleration
- **PyMuPDF** & **PaddleOCR** - Document processing

Special thanks to public archives like **epstein-files.org**, **Librarius**, and **ErikVeland/epstein-archive** for demonstrating the value of open research.

---

## ⚠️ Responsible Use

SPECTOR is a research tool. Use it responsibly:

- ✅ **Respect robots.txt** and website terms of service
- ✅ **Rate limit** your requests (default: 1 req/sec)
- ✅ **Public documents only** - never access restricted systems
- ✅ **Comply with GDPR/CCPA** if deploying publicly
- ✅ **Attribute sources** appropriately in research

See [DISCLAIMER_OSS.md](DISCLAIMER_OSS.md) for complete legal guidelines.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR-USERNAME/SPECTOR/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR-USERNAME/SPECTOR/discussions)
- **Security**: See [SECURITY.md](SECURITY.md) for vulnerability reporting

---

**Built with ❤️ by the open-source community**

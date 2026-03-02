# SPECTOR Installation Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | 3.12 recommended |
| Julia | 1.9+ | 1.10 LTS recommended |
| Docker + Compose | 24.x+ | For infrastructure services |
| NVIDIA GPU | Optional | CUDA 12.x/13.x for acceleration |

## Quick Install (Docker -- Recommended)

```bash
git clone https://github.com/blkout-hd/ep_spector.git
cd ep_spector

# Copy and fill in all environment secrets
cp .env.example .env
# Edit .env -- set all passwords, API keys, Neo4j credentials

# Start all infrastructure services
docker compose up -d

# Verify all services are healthy
docker compose ps
```

## Python Installation

```bash
# Standard install (CPU only)
pip install -e .

# GPU install (CUDA 13.x)
pip install -e ".[cuda13x]"

# GPU install (CUDA 12.x)
pip install -e ".[cuda12x]"

# Development dependencies
pip install -e ".[dev]"

# Download spaCy model
python -m spacy download en_core_web_lg
```

## Julia Installation

```bash
# Download Julia 1.10 LTS from https://julialang.org/downloads/

# Install SPECTOR Julia dependencies
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

## Environment Variables

Copy `.env.example` to `.env` and set all required values.
**Never commit `.env` to version control.**

Required variables:

```
NEO4J_PASSWORD=         # Min 12 chars
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
POSTGRES_USER=spector
POSTGRES_PASSWORD=      # Min 12 chars
POSTGRES_DB=spector
REDIS_PASSWORD=         # Min 16 chars
MONGO_USER=spector
MONGO_PASSWORD=         # Min 12 chars
QDRANT_API_KEY=         # Min 32 chars
CHROMA_TOKEN=           # Min 32 chars
DJANGO_SECRET_KEY=      # Min 50 chars random string
```

## Running Tests

```bash
# Python test suite
pytest tests/python/ -v

# Julia test suite
julia --project=. tests/julia/runtests.jl
```

## Verifying Installation

```bash
# Check system capabilities
python -m spector

# Start admin console (default http://localhost:8888)
python launcher.py admin --port 8888
```

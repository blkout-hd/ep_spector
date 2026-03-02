# Changelog

All notable changes to SPECTOR are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased] — 2026-03-02

### Added
- `agents/pipeline/state.py` — `PipelineState` TypedDict with full field set and `operator.add` accumulator for `completed_stages`
- `agents/pipeline/graph.py` — LangGraph `StateGraph` wiring ingest → ner → embed → kg → manifold with conditional error short-circuit
- `agents/runner.py` — Redis `BRPOP` worker loop; persists results to `spector:result:<hash>` with 24h TTL
- `src/python/spector_django/settings.py` — Environment-only Django settings with Redis cache, Channels layer, DRF throttling
- `src/python/spector_django/urls.py` — Root URL config: admin, health, documents, entities, privacy, api-auth
- `src/python/spector_django/wsgi.py` — WSGI entrypoint
- `src/python/spector_django/asgi.py` — ASGI + Django Channels WebSocket bootstrap
- `src/python/spector_django/apps/documents/` — `Document` model, DRF serializer, list/detail/ingest/status views, URL routing
- `src/python/spector_django/apps/entities/` — `Entity` model, serializer, list/detail views
- `src/python/spector_django/apps/privacy/` — GDPR Art. 17 / CCPA erasure endpoint; audit-logged
- `tests/python/conftest.py` — Shared fixtures: `sample_pdf_text`, `embed_agent`
- `tests/python/test_ingest_agent.py` — 4 unit tests: hash determinism, bad path, full_text, no-hidden
- `tests/python/test_ner_agent.py` — 4 unit tests: person extraction, empty input, dedup, normalization
- `tests/python/test_embed_agent.py` — 4 unit tests: shape, empty, delta norm, unit length
- `tests/python/test_pipeline.py` — 2 integration tests: state shape, graph compile
- `tests/julia/runtests.jl` — 4 Julia testsets: SpectorGraph, suppression_score, BFS, probe fallback
- `INSTALL.md` — Full installation guide (Docker, Python, Julia, env vars, test commands)
- `UPDATE_BRIEF.md` — Session update brief
- `CHANGELOG.md` — This file

---

## [1.0.0-dev.8] — 2026-03-02 `c0dbf59`

### Fixed
- `pyproject.toml` — Corrected all `[project.urls]` from placeholder values to `https://github.com/blkout-hd/ep_spector`

---

## [1.0.0-dev.7] — 2026-03-02 `c57ee8f`

### Changed
- `src/julia/SPECTOR.jl` — Renamed `suppression_score` to `embedding_delta_norm` throughout to match mathematical semantics (L2 norm of embedding delta vector)

### Added
- Academic citations in `SPECTOR.jl` docstrings: McInnes et al. 2018 (UMAP), Campello et al. 2013 (HDBSCAN)

---

## [1.0.0-dev.6] — 2026-03-02 `4056ead`

### Fixed
- `README.md` — Removed `goyfiles.com` from Acknowledgments section
- `README.md` — Corrected repository clone URL and all internal links to point to `blkout-hd/ep_spector`

---

## [1.0.0-dev.5] — 2026-03-02 `fe24ce5`

### Added
- `mcp_servers/doc_search_server.py` — MCP tool: semantic document search via Qdrant
- `mcp_servers/kg_query_server.py` — MCP tool: Neo4j Cypher query via natural language
- `mcp_servers/media_index_server.py` — MCP tool: media probe inventory
- `mcp_servers/smithery.yaml` — Smithery registry manifest
- `scripts/bootstrap.py` — GPU-aware capability probe; auto-installs CUDA extras

### Fixed
- `src/julia/SPECTOR.jl` — Removed broken `Async`, `LightGraphs`, `TSNE` imports; replaced with correct Julia stdlib/registered equivalents
- `tests/` — Added `conftest.py` + smoke tests for all 4 critical paths (ingest, NER, embed, KG)

---

## [1.0.0-dev.4] — 2026-03-02 `775aa51`

### Added
- `src/python/spector_django/` — Initial Django project scaffold
- `apps/documents/` — `Document` model + DRF serializer + REST views
- `apps/privacy/` — GDPR data subject erasure endpoint
- `apps/entities/` — Entity model stub
- `manage.py` — Django management entry point

---

## [1.0.0-dev.3] — 2026-03-02 `f256d00`

### Added
- `agents/ingest_agent.py` — PyMuPDF hidden-layer extraction + PaddleOCR fallback for scanned pages
- `agents/ner_agent.py` — spaCy + GLiNER two-pass NER with confidence scoring and deduplication
- `agents/embed_agent.py` — BGE-M3 / sentence-transformers encoder; L2 embedding delta norm
- `agents/media_probe_agent.py` — Async aiohttp rate-limited extension cycling with Tor proxy support
- `agents/kg_expand_agent.py` — Neo4j Cypher batch write + BFS frontier expansion
- `agents/manifold_agent.py` — cuML/scikit-learn UMAP + HDBSCAN clustering; GPU-adaptive
- `agents/diff_proxy_agent.py` — Embedding delta suppression scoring between document versions
- `agents/__init__.py` — Registry export for all agent classes

---

## [1.0.0-dev.2] — 2026-03-02 `e137401`

### Added
- `agents/pipeline/state.py` — `PipelineState` TypedDict (initial version)
- `agents/pipeline/graph.py` — LangGraph `StateGraph` initial wiring
- `agents/pipeline/checkpointer.py` — SQLite-backed checkpoint persistence
- `agents/pipeline/runner.py` — CLI entrypoint for graph execution
- `agents/pipeline/__init__.py` — Public exports

---

## [1.0.0-dev.1] — 2026-03-02 `29112b3`

### Added
- `Dockerfile.django` — Multi-stage Django/Gunicorn image; non-root user; health check on `/api/health/`
- `Dockerfile.tornado` — Lightweight Tor-capable admin console image
- `Dockerfile.worker` — GPU-aware LangGraph agent worker; embeds Julia 1.10 LTS install

### Fixed
- Resolved `docker compose build` failures for all three custom services in `docker-compose.yml`

---

## [1.0.0-alpha] — 2026-02-24 `7d510de`

### Added
- Initial public commit: SPECTOR v1.0.0 forensically sanitized
- Complete document analysis framework skeleton
- Knowledge graph integration stubs
- Vector search capability stubs
- Tor network support via `stem` + `PySocks`
- Pre-commit security hooks (gitleaks, trufflehog, detect-secrets)
- `pyproject.toml` with full dependency manifest
- `Project.toml` with Julia dependency manifest
- `docker-compose.yml` — Full infrastructure stack (Neo4j, Qdrant, Redis, MongoDB, PostgreSQL, Chroma)
- `.env.example` — Reference environment variable template
- `launcher.py` — CLI launcher with AI provider detection
- `robots.txt` — Crawl restrictions
- `DISCLAIMER.md` — Legal framework and usage restrictions
- `CONTRIBUTING.md` — Contribution guidelines
- `SECURITY.md` — Security policy and disclosure process
- `LICENSE` (MIT) + `LICENSE-AGPL` + `LICENSE-MIT`
- `README.md` — Full project documentation

### Removed (2026-02-24 cleanup, `51db028` → `a6c22cb`)
- 28 internal planning/assessment documents
- Legal risk assessment documents
- OSS release planning docs
- Security audit internal docs
- `TODO.md`, `AGENTS.md`, `ARCHITECTURE.md` (pending restore)
- Internal execution scripts
- `.qwen/` directory

---

[Unreleased]: https://github.com/blkout-hd/ep_spector/compare/v1.0.0-alpha...HEAD
[1.0.0-alpha]: https://github.com/blkout-hd/ep_spector/commit/7d510dea2b1eaa32d71d0ae48de1a51cb4cd4504

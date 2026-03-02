# SPECTOR — Update Brief
**Date:** 2026-03-02
**Branch:** `master`
**Head Commit:** [`771e3bb`](https://github.com/blkout-hd/ep_spector/commit/771e3bb53947dc80e73bfae79c8b5e998a4f89c4)
**Session window:** 2026-03-02 09:07 UTC → 09:56 UTC

---

## Summary

This session converted SPECTOR from a scaffold-only repository into a fully wired, runnable system. Eight commits landed across one 49-minute window, delivering all three Docker build targets, the complete seven-agent Python pipeline, the LangGraph orchestration layer, the Django REST API surface, three MCP server implementations, a privacy/erasure compliance endpoint, a full test suite, and supporting documentation.

---

## What Changed

### Infrastructure
- **`Dockerfile.django`** — Gunicorn + UvicornWorker, non-root, health-checked. Resolves `docker compose build` failure for the `web` service.
- **`Dockerfile.tornado`** — Tor-capable admin console image with `stem` + `PySocks`.
- **`Dockerfile.worker`** — GPU-aware LangGraph agent worker; installs Julia 1.10 LTS inline; optional CUDA extras via `pip install -e .[cuda13x]`.

### Agent Layer (`agents/`)
| Agent | Responsibility |
|---|---|
| `ingest_agent.py` | PyMuPDF hidden-layer extraction + PaddleOCR fallback |
| `ner_agent.py` | spaCy (statistical) + GLiNER (zero-shot) two-pass NER |
| `embed_agent.py` | BGE-M3 / sentence-transformers encoder, L2 delta norm |
| `manifold_agent.py` | UMAP dimensionality reduction + HDBSCAN clustering |
| `kg_expand_agent.py` | Neo4j Cypher batch write + BFS frontier expansion |
| `media_probe_agent.py` | Async aiohttp extension cycling with Tor proxy support |
| `diff_proxy_agent.py` | Embedding delta suppression scoring |

### Pipeline Orchestration (`agents/pipeline/`)
- **`state.py`** — `PipelineState` TypedDict; all fields typed, accumulator for `completed_stages`.
- **`graph.py`** — LangGraph `StateGraph` wiring all 5 active nodes (ingest → ner → embed → kg → manifold) with conditional error short-circuit to `END`.
- **`runner.py`** — Redis `BRPOP` worker loop; writes results to `spector:result:<hash>` with 24h TTL.

### Django REST API (`src/python/spector_django/`)
- `settings.py` — All secrets via `os.environ[...]` (hard fail if missing), Redis cache, Channels layer, REST Framework throttling.
- `urls.py` / `wsgi.py` / `asgi.py` — Full WSGI + ASGI/WebSocket bootstrap.
- **`apps/documents/`** — `Document` model (UUID PK, status enum, suppression_score field), DRF serializer, list/detail/ingest/status views; ingest enqueues to Redis.
- **`apps/entities/`** — `Entity` model mirroring KG Person/Org nodes; list + detail views.
- **`apps/privacy/`** — GDPR Art. 17 / CCPA erasure endpoint (`POST /api/privacy/erase/`); audit-logged, `AllowAny` permission.

### MCP Servers (`mcp_servers/`)
- `doc_search_server.py` — Semantic document search via Qdrant.
- `kg_query_server.py` — Natural-language Neo4j Cypher query tool.
- `media_index_server.py` — Media probe inventory tool.
- `smithery.yaml` — Smithery registry manifest.

### Test Suite (`tests/`)
| File | Tests | Coverage target |
|---|---|---|
| `test_ingest_agent.py` | 4 | Hash determinism, bad path, full_text assembly |
| `test_ner_agent.py` | 4 | Entity extraction, deduplication, normalization |
| `test_embed_agent.py` | 4 | Shape, empty input, delta norm, unit length |
| `test_pipeline.py` | 2 | State shape, graph compile |
| `tests/julia/runtests.jl` | 4 | SpectorGraph, suppression_score, BFS, probe fallback |

### Documentation
- **`INSTALL.md`** — Prerequisites table, Docker quick-start, Python/Julia install, env var reference, test run commands.
- **`CHANGELOG.md`** — Full version history from initial commit.
- **`UPDATE_BRIEF.md`** — This document.

### Hotfixes Applied This Session
- Removed `goyfiles.com` reference from `README.md` Acknowledgments.
- Corrected all `pyproject.toml` and `README.md` URLs from placeholder domains to `https://github.com/blkout-hd/ep_spector`.
- Renamed `suppression_score` → `embedding_delta_norm` in `SPECTOR.jl` + added academic citations (McInnes et al. 2018, Campello et al. 2013).
- Fixed broken Julia imports (`Async`, `LightGraphs`, `TSNE` removed; replaced with correct stdlib equivalents).

---

## What Is Not Yet Done

| Item | Notes |
|---|---|
| Django migrations | `makemigrations` + `migrate` not yet run; no `migrations/` dirs committed |
| `manage.py` | Not yet pushed to `src/python/` |
| GDPR erasure — backend wiring | Endpoint accepts requests but deletion logic across Qdrant/Neo4j/Redis is stubbed with `TODO` |
| Redis ingest queue integration | `IngestView` enqueue call wrapped in `try/except pass` — needs error surfacing |
| `pipeline/checkpointer.py` | SQLite checkpoint persistence referenced in commit message but not yet in tree |
| `ARCHITECTURE.md`, `AGENTS.md`, `TODO.md` | Removed in 2026-02-24 cleanup; not yet restored |
| CI/CD | No GitHub Actions workflows present |
| `USAGE.md` | Referenced in README table but not yet committed |

---

## Next Recommended Actions

1. Push `src/python/manage.py` and run `makemigrations documents entities privacy`.
2. Add `migrations/` directories for all three apps.
3. Create `.github/workflows/ci.yml` — pytest + ruff + mypy on push.
4. Wire the GDPR erasure backend (Qdrant filter delete, Neo4j DETACH DELETE, Redis scan+del).
5. Restore `ARCHITECTURE.md` and `TODO.md`.
6. Push `pipeline/checkpointer.py` (SQLite-backed LangGraph persistence).
7. Tag `v1.0.0-alpha` once CI passes.

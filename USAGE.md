# SPECTOR Usage Guide

This guide assumes you have followed `INSTALL.md` and have all services running.

## 1. Start the stack

```bash
cp .env.example .env   # fill in secrets
docker compose up -d
python launcher.py admin --port 8888 --host localhost
```

## 2. Ingest a document

```bash
# By URL
curl -X POST http://localhost:8000/api/documents/ingest/ \
  -H "Content-Type: application/json" \
  -d '{"source_url": "https://example.com/doc.pdf"}'
```

The response contains an `id` (UUID) and initial `status` (`pending`).

## 3. Check document status

```bash
curl http://localhost:8000/api/documents/status/<uuid>/
```

Statuses:

- `pending`: queued, not yet picked up.
- `processing`: being handled by the worker.
- `complete`: pipeline finished successfully.
- `failed`: error encountered; see `error_message`.

## 4. List documents and entities

```bash
# Documents
curl http://localhost:8000/api/documents/

# Entities
curl http://localhost:8000/api/entities/
```

Use query parameters such as `?label=PERSON` or `?status=complete`
for basic filtering.

## 5. Issue a GDPR/CCPA erasure request

```bash
curl -X POST http://localhost:8000/api/privacy/erase/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "Jane Doe"}'
```

This deletes matching `Entity` rows and marks documents that contain
the identifier in `raw_text`. External vector/graph stores require
operator-side configuration.

## 6. Running tests

```bash
# Python tests
pytest tests/python/ -v

# Julia tests
julia --project=. tests/julia/runtests.jl
```

## 7. Operating the worker

The agent worker consumes from Redis and runs the LangGraph pipeline:

```bash
python -m agents.runner
```

Configure checkpointing via:

- `SPECTOR_CHECKPOINTER=memory` (default)
- `SPECTOR_CHECKPOINTER=sqlite`
- `SPECTOR_CHECKPOINT_DB=data/checkpoints.sqlite`

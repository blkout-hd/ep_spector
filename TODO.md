# SPECTOR TODO / Roadmap

This file tracks high-level tasks. For granular issues, use GitHub issues.

## Short Term

- [x] Wire LangGraph checkpointer abstraction (memory / SQLite).
- [x] Add Django migrations for `documents` and `entities`.
- [ ] Implement external erasure wiring (Qdrant, Neo4j, Redis) in privacy app.
- [ ] Expand test coverage for Django API endpoints.
- [ ] Add smoke tests for MCP servers.

## Medium Term

- [ ] Restore and expand product documentation (user personas, threat model).
- [ ] Add Grafana/Prometheus integration for worker and admin console.
- [ ] Implement rate limiting and IP-based throttling for public endpoints.
- [ ] Add bulk import tooling for large FOIA/PACER corpora.

## Long Term

- [ ] Multi-tenant workspace support.
- [ ] Interactive graph exploration UI.
- [ ] Pluggable entity resolution backends.
- [ ] Improved differential privacy for analytics workloads.

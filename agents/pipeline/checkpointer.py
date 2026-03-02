"""
LangGraph checkpointer configuration for SPECTOR.

Default: in-memory checkpoints (safe for dev / tests).
Optional: SQLite persistence when SPECTOR_CHECKPOINTER=sqlite
and langgraph-checkpoint-sqlite is installed.

Env vars:
- SPECTOR_CHECKPOINTER: "memory" (default) or "sqlite"
- SPECTOR_CHECKPOINT_DB: path to SQLite file (default: data/checkpoints.sqlite)
"""
from __future__ import annotations

import logging
import os

from langgraph.checkpoint.memory import InMemorySaver

logger = logging.getLogger(__name__)

try:
    # Requires extra package: langgraph-checkpoint-sqlite
    from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore[import]
except Exception:  # pragma: no cover - optional dependency
    SqliteSaver = None  # type: ignore[assignment]


def get_checkpointer():
    """Return a LangGraph checkpointer instance.

    - In all environments: in-memory saver is always available.
    - If SPECTOR_CHECKPOINTER=sqlite and SqliteSaver is importable,
      use SQLite-backed persistence.

    This function never raises on missing optional deps; it logs and
    falls back to in-memory.
    """
    backend = os.getenv("SPECTOR_CHECKPOINTER", "memory").lower()

    if backend == "sqlite":
        if SqliteSaver is None:
            logger.warning(
                "SPECTOR_CHECKPOINTER=sqlite but langgraph-checkpoint-sqlite "
                "is not installed; falling back to in-memory saver."
            )
        else:
            import sqlite3

            db_path = os.getenv("SPECTOR_CHECKPOINT_DB", "data/checkpoints.sqlite")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path, check_same_thread=False)
            logger.info("Using SQLite checkpointer at %s", db_path)
            return SqliteSaver(conn)

    logger.info("Using in-memory LangGraph checkpointer")
    return InMemorySaver()

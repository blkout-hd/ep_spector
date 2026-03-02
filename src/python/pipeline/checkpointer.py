"""
LangGraph SQLite Checkpointer for SPECTOR pipeline.

Persists graph state between runs so interrupted pipelines
can resume from the last completed node rather than restarting.
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger("spector.pipeline.checkpointer")

DEFAULT_DB = Path.home() / ".spector" / "checkpoints.db"


def get_checkpointer(db_path: Optional[Path] = None):
    """
    Return a LangGraph SqliteSaver checkpointer.

    Args:
        db_path: Path to SQLite file. Defaults to ~/.spector/checkpoints.db

    Returns:
        SqliteSaver instance ready for use in StateGraph.compile(checkpoint=...)
    """
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError:
        # langgraph >= 0.2 moved the import
        from langgraph.checkpoint import SqliteSaver  # type: ignore

    path = db_path or DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path), check_same_thread=False)
    logger.info("Checkpoint DB: %s", path)
    return SqliteSaver(conn)

"""
Smoke tests for ingest_agent
"""
from __future__ import annotations

import os
import tempfile

import pytest


def test_ingest_local_text_file():
    """Ingest a local text file and confirm doc record returned."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))
    from ingest_agent import run

    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("Test document content about public records.")
        path = f.name

    try:
        result = run({"source_urls": [path], "use_tor": False})
        assert "documents" in result
        assert len(result["documents"]) == 1
        assert result["documents"][0]["raw_text"] == "Test document content about public records."
    finally:
        os.unlink(path)


def test_ingest_missing_source_returns_error():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))
    from ingest_agent import run

    result = run({"source_urls": ["/nonexistent/file.pdf"], "use_tor": False})
    assert len(result["errors"]) >= 1


def test_ingest_no_sources():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))
    from ingest_agent import run

    result = run({})
    assert result["documents"] == []

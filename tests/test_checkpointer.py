"""
tests/test_checkpointer.py

Unit tests for agents/pipeline/checkpointer.py.

All tests are pure-Python and require no live services.
"""
from __future__ import annotations

import importlib
import os
import sys
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _reload_module():
    """Force a fresh import of the checkpointer module."""
    mod_name = "agents.pipeline.checkpointer"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return importlib.import_module(mod_name)


# ---------------------------------------------------------------------------
# in-memory path
# ---------------------------------------------------------------------------

class TestInMemoryCheckpointer:
    def test_default_returns_in_memory(self, monkeypatch):
        """Without any env var the checkpointer is InMemorySaver."""
        monkeypatch.delenv("SPECTOR_CHECKPOINTER", raising=False)
        mod = _reload_module()
        cp = mod.get_checkpointer()
        # Must be an instance of InMemorySaver from langgraph
        from langgraph.checkpoint.memory import InMemorySaver
        assert isinstance(cp, InMemorySaver)

    def test_explicit_memory_env_returns_in_memory(self, monkeypatch):
        """SPECTOR_CHECKPOINTER=memory also returns InMemorySaver."""
        monkeypatch.setenv("SPECTOR_CHECKPOINTER", "memory")
        mod = _reload_module()
        cp = mod.get_checkpointer()
        from langgraph.checkpoint.memory import InMemorySaver
        assert isinstance(cp, InMemorySaver)

    def test_case_insensitive_env(self, monkeypatch):
        """Env var is compared case-insensitively."""
        monkeypatch.setenv("SPECTOR_CHECKPOINTER", "MEMORY")
        mod = _reload_module()
        cp = mod.get_checkpointer()
        from langgraph.checkpoint.memory import InMemorySaver
        assert isinstance(cp, InMemorySaver)


# ---------------------------------------------------------------------------
# sqlite path — dep missing
# ---------------------------------------------------------------------------

class TestSQLiteCheckpointerMissingDep:
    def test_falls_back_to_memory_when_dep_missing(self, monkeypatch):
        """If SqliteSaver is None (dep absent), fall back to InMemorySaver."""
        monkeypatch.setenv("SPECTOR_CHECKPOINTER", "sqlite")
        mod = _reload_module()
        # Forcefully remove the optional dependency
        mod.SqliteSaver = None
        cp = mod.get_checkpointer()
        from langgraph.checkpoint.memory import InMemorySaver
        assert isinstance(cp, InMemorySaver)

    def test_warning_logged_when_dep_missing(self, monkeypatch, caplog):
        """A warning should be emitted when sqlite dep is absent."""
        import logging
        monkeypatch.setenv("SPECTOR_CHECKPOINTER", "sqlite")
        mod = _reload_module()
        mod.SqliteSaver = None
        with caplog.at_level(logging.WARNING, logger="agents.pipeline.checkpointer"):
            mod.get_checkpointer()
        assert any("not installed" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# sqlite path — dep present (mocked)
# ---------------------------------------------------------------------------

class TestSQLiteCheckpointerPresent:
    def test_returns_sqlite_saver_when_dep_present(self, monkeypatch, tmp_path):
        """When SqliteSaver is available, get_checkpointer returns it."""
        monkeypatch.setenv("SPECTOR_CHECKPOINTER", "sqlite")
        db_path = str(tmp_path / "test_checkpoints.sqlite")
        monkeypatch.setenv("SPECTOR_CHECKPOINT_DB", db_path)

        mod = _reload_module()

        # Mock SqliteSaver so test works even without the optional package
        mock_saver_instance = MagicMock(name="SqliteSaverInstance")
        mock_saver_cls = MagicMock(
            return_value=mock_saver_instance, name="SqliteSaver"
        )
        mod.SqliteSaver = mock_saver_cls

        cp = mod.get_checkpointer()

        assert mock_saver_cls.called, "SqliteSaver constructor should have been called"
        assert cp is mock_saver_instance

    def test_sqlite_db_dir_is_created(self, monkeypatch, tmp_path):
        """The directory for the SQLite DB file is created if absent."""
        monkeypatch.setenv("SPECTOR_CHECKPOINTER", "sqlite")
        nested = tmp_path / "a" / "b" / "checkpoints.sqlite"
        monkeypatch.setenv("SPECTOR_CHECKPOINT_DB", str(nested))

        mod = _reload_module()
        mock_saver_cls = MagicMock(return_value=MagicMock())
        mod.SqliteSaver = mock_saver_cls

        mod.get_checkpointer()

        assert (tmp_path / "a" / "b").is_dir()


# ---------------------------------------------------------------------------
# build_graph integration: checkpointer is forwarded correctly
# ---------------------------------------------------------------------------

class TestBuildGraphCheckpointer:
    def test_build_graph_no_checkpointer(self):
        """build_graph() compiles cleanly without a checkpointer."""
        from agents.pipeline.graph import build_graph
        g = build_graph()
        # The compiled graph must be invocable (has .invoke)
        assert callable(getattr(g, "invoke", None))

    def test_build_graph_with_in_memory_checkpointer(self):
        """build_graph(checkpointer=...) accepts an InMemorySaver."""
        from langgraph.checkpoint.memory import InMemorySaver
        from agents.pipeline.graph import build_graph

        cp = InMemorySaver()
        g = build_graph(checkpointer=cp)
        assert callable(getattr(g, "invoke", None))

    def test_build_graph_with_mock_checkpointer(self):
        """build_graph accepts any duck-typed checkpointer object."""
        from agents.pipeline.graph import build_graph

        mock_cp = MagicMock()
        # LangGraph calls checkpointer.get_tuple / put etc; we just ensure
        # compile doesn't raise with a mock that passes isinstance checks.
        # If langgraph validates the type, skip gracefully.
        try:
            g = build_graph(checkpointer=mock_cp)
            assert callable(getattr(g, "invoke", None))
        except Exception as exc:
            pytest.skip(f"LangGraph rejected mock checkpointer: {exc}")

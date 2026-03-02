"""Shared pytest fixtures for SPECTOR test suite."""
import pytest


@pytest.fixture
def sample_pdf_text():
    return (
        "Jeffrey Epstein was associated with Ghislaine Maxwell. "
        "Epstein flew on a Gulfstream IV registered to Southern Trust Company. "
        "The Palm Beach estate at 358 El Brillo Way was a central location."
    )


@pytest.fixture
def embed_agent():
    from agents.embed_agent import EmbedAgent
    return EmbedAgent(model_name="sentence-transformers/all-MiniLM-L6-v2")

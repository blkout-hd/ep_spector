"""
SPECTOR Agent Registry

All pipeline agents are registered here for discovery.
Each module exposes a `run(state: PipelineState) -> dict` function.
"""
from importlib import import_module

AGENT_MODULES = [
    "ingest_agent",
    "ner_agent",
    "embed_agent",
    "media_probe_agent",
    "kg_expand_agent",
    "manifold_agent",
    "diff_proxy_agent",
]

__all__ = AGENT_MODULES

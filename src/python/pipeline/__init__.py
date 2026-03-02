"""
SPECTOR Pipeline Orchestration

LangGraph-based StateGraph wiring ingest → NER → embed → KG → manifold → diff.
"""
from .state import PipelineState
from .graph import build_graph
from .runner import run_pipeline

__all__ = ["PipelineState", "build_graph", "run_pipeline"]

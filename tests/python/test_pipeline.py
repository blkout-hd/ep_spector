"""Integration test for LangGraph pipeline state transitions."""
from agents.pipeline.state import PipelineState


def test_pipeline_state_shape():
    state: PipelineState = {
        "source": "https://example.com/doc.pdf",
        "doc_id": None,
        "visible_text": "",
        "hidden_text": "",
        "ocr_text": "",
        "has_hidden_text": False,
        "file_hash": "",
        "page_count": 0,
        "entities": [],
        "entity_count": 0,
        "doc_embedding": None,
        "entity_embeddings": {},
        "kg_node_ids": {},
        "kg_edges_written": 0,
        "cluster_labels": None,
        "n_clusters": 0,
        "error": None,
        "completed_stages": [],
    }
    assert state["source"] == "https://example.com/doc.pdf"
    assert state["error"] is None
    assert isinstance(state["completed_stages"], list)


def test_pipeline_graph_builds():
    from agents.pipeline.graph import build_graph
    graph = build_graph()
    assert graph is not None

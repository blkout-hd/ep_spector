"""
SPECTOR KG Expand Agent

Writes entities and their co-occurrence relationships to Neo4j,
then optionally calls into Julia's BFS expansion to discover
second-degree connections across the knowledge graph.

Neo4j schema follows docs/KG_SCHEMA.md:
  - (:Entity {id, label, text, doc_id, confidence})
  - (:Document {id, source_url, pages})
  - (:Entity)-[:CO_OCCURS_IN]->(:Document)
  - (:Entity)-[:CO_OCCURS_WITH {weight}]->(:Entity)
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("spector.agents.kg_expand")

_driver = None


def _get_driver():
    global _driver
    if _driver is None:
        from neo4j import GraphDatabase
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "spector")
        _driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("Neo4j driver connected: %s", uri)
    return _driver


_MERGE_DOCUMENT = """
MERGE (d:Document {id: $doc_id})
SET d.source_url = $source_url,
    d.pages = $pages,
    d.updated_at = timestamp()
RETURN d
"""

_MERGE_ENTITY = """
MERGE (e:Entity {id: $entity_id})
SET e.label = $label,
    e.text = $text,
    e.confidence = $confidence
RETURN e
"""

_MERGE_CO_OCCURS_IN = """
MATCH (e:Entity {id: $entity_id})
MATCH (d:Document {id: $doc_id})
MERGE (e)-[:CO_OCCURS_IN]->(d)
"""

_MERGE_CO_OCCURS_WITH = """
UNWIND $pairs AS pair
MATCH (a:Entity {id: pair.a})
MATCH (b:Entity {id: pair.b})
MERGE (a)-[r:CO_OCCURS_WITH]-(b)
ON CREATE SET r.weight = 1
ON MATCH SET r.weight = r.weight + 1
"""


def _write_batch(session, docs: list, entities: list) -> tuple[int, int]:
    """Write a batch of docs and entities. Returns (nodes, edges) written."""
    nodes = 0
    edges = 0

    # Write documents
    for doc in docs:
        session.run(_MERGE_DOCUMENT,
                    doc_id=doc.get("doc_id"),
                    source_url=doc.get("source_url", ""),
                    pages=doc.get("pages", 0))
        nodes += 1

    # Write entities and doc-entity edges
    for ent in entities:
        session.run(_MERGE_ENTITY,
                    entity_id=ent.get("entity_id"),
                    label=ent.get("label", ""),
                    text=ent.get("text", ""),
                    confidence=ent.get("confidence", 0.0))
        nodes += 1
        session.run(_MERGE_CO_OCCURS_IN,
                    entity_id=ent.get("entity_id"),
                    doc_id=ent.get("doc_id"))
        edges += 1

    # Write entity co-occurrence edges (within same document)
    from itertools import combinations
    by_doc: dict[str, list] = {}
    for ent in entities:
        by_doc.setdefault(ent.get("doc_id", ""), []).append(ent.get("entity_id"))

    for doc_id, ent_ids in by_doc.items():
        pairs = [{"a": a, "b": b} for a, b in combinations(ent_ids[:50], 2)]
        if pairs:
            session.run(_MERGE_CO_OCCURS_WITH, pairs=pairs)
            edges += len(pairs)

    return nodes, edges


def run(state: dict) -> dict:
    """
    Pipeline node: write entities + documents to Neo4j KG.

    Returns dict patch:
      - kg_nodes_written: int
      - kg_edges_written: int
      - errors: list[str]
    """
    docs = state.get("documents", [])
    entities = state.get("entities", [])
    errors = []
    total_nodes = 0
    total_edges = 0

    try:
        driver = _get_driver()
        with driver.session() as session:
            nodes, edges = _write_batch(session, docs, entities)
            total_nodes += nodes
            total_edges += edges
    except Exception as exc:
        logger.error("Neo4j write failed: %s", exc)
        errors.append(f"kg_expand:{exc}")

    logger.info("KG write: %d nodes, %d edges", total_nodes, total_edges)
    return {
        "kg_nodes_written": total_nodes,
        "kg_edges_written": total_edges,
        "errors": errors,
    }

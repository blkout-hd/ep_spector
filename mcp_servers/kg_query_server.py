"""
SPECTOR MCP Server — Knowledge Graph Query

Exposes two MCP tools:
  - query_knowledge_graph: Run arbitrary Cypher read queries
  - get_entity_connections: Get all connections for a named entity
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("spector.mcp.kg_query")

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


def _run_cypher(query: str, params: dict | None = None) -> list[dict]:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        auth=(
            os.environ.get("NEO4J_USER", "neo4j"),
            os.environ.get("NEO4J_PASSWORD", "spector"),
        ),
    )
    with driver.session() as session:
        result = session.run(query, parameters=params or {})
        return [dict(record) for record in result]


def create_server() -> "Server":
    if not MCP_AVAILABLE:
        raise RuntimeError("mcp package required")

    server = Server("spector-kg-query")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="query_knowledge_graph",
                description="Run a read-only Cypher query against the SPECTOR Neo4j knowledge graph.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cypher": {"type": "string", "description": "Cypher READ query"},
                    },
                    "required": ["cypher"],
                },
            ),
            Tool(
                name="get_entity_connections",
                description="Get all entities co-occurring with a named entity in the KG.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "entity_text": {"type": "string"},
                        "depth": {"type": "integer", "default": 2},
                    },
                    "required": ["entity_text"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]):
        if name == "query_knowledge_graph":
            cypher = arguments["cypher"]
            if any(kw in cypher.upper() for kw in ("CREATE", "MERGE", "DELETE", "SET", "DROP")):
                return [TextContent(type="text", text="Error: Only READ queries are permitted.")]
            rows = _run_cypher(cypher)
            return [TextContent(type="text", text=str(rows[:50]))]

        if name == "get_entity_connections":
            text = arguments["entity_text"]
            depth = arguments.get("depth", 2)
            cypher = (
                f"MATCH p=(e:Entity {{text: $text}})-[:CO_OCCURS_WITH*1..{depth}]-(other) "
                "RETURN other.text AS entity, other.label AS label, "
                "length(p) AS distance ORDER BY distance LIMIT 50"
            )
            rows = _run_cypher(cypher, {"text": text})
            lines = [f"{r['entity']} [{r['label']}] distance={r['distance']}" for r in rows]
            return [TextContent(type="text", text="\n".join(lines) or "No connections found.")]

        raise ValueError(f"Unknown tool: {name}")

    return server


async def main():
    server = create_server()
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

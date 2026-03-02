"""
SPECTOR MCP Server — Document Search

Exposes a single MCP tool: search_documents
Allows MCP-compatible AI clients (Claude, Copilot, etc.) to query
the SPECTOR document index via semantic similarity search.
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("spector.mcp.doc_search")

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("mcp package not installed; doc_search_server unavailable")


def _search_qdrant(query: str, top_k: int = 10) -> list[dict]:
    """Perform semantic search against Qdrant collection."""
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    client = QdrantClient(
        host=os.environ.get("QDRANT_HOST", "localhost"),
        port=int(os.environ.get("QDRANT_PORT", "6333")),
    )
    encoder = SentenceTransformer(
        os.environ.get("SPECTOR_EMBED_MODEL", "all-MiniLM-L6-v2")
    )
    vector = encoder.encode(query, normalize_embeddings=True).tolist()

    results = client.search(
        collection_name="spector_documents",
        query_vector=vector,
        limit=top_k,
        with_payload=True,
    )
    return [
        {
            "doc_id": r.payload.get("doc_id"),
            "source_url": r.payload.get("source_url"),
            "score": r.score,
            "snippet": r.payload.get("raw_text", "")[:500],
        }
        for r in results
    ]


def create_server() -> "Server":
    if not MCP_AVAILABLE:
        raise RuntimeError("mcp package required")

    server = Server("spector-doc-search")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="search_documents",
                description=(
                    "Semantically search the SPECTOR document index. "
                    "Returns top matching documents from the Epstein files corpus "
                    "and other ingested public document sets."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "top_k": {"type": "integer", "default": 10, "description": "Max results"},
                    },
                    "required": ["query"],
                },
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]):
        if name == "search_documents":
            query = arguments["query"]
            top_k = arguments.get("top_k", 10)
            results = _search_qdrant(query, top_k)
            text = "\n\n".join(
                f"[{r['score']:.3f}] {r['source_url']}\n{r['snippet']}"
                for r in results
            )
            return [TextContent(type="text", text=text or "No results found.")]
        raise ValueError(f"Unknown tool: {name}")

    return server


async def main():
    server = create_server()
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

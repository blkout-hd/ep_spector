"""
SPECTOR MCP Server — Media Index

Exposes: list_media_probes, get_media_by_doc

Allows AI clients to query which media files were discovered
during extension probing of source document URLs.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("spector.mcp.media_index")

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


def _load_probes() -> list[dict]:
    """Load saved media probe results from disk cache."""
    cache_path = Path(os.environ.get("SPECTOR_PROBE_CACHE",
                                     Path.home() / ".spector" / "media_probes.json"))
    if not cache_path.exists():
        return []
    with open(cache_path) as fh:
        return json.load(fh)


def create_server() -> "Server":
    if not MCP_AVAILABLE:
        raise RuntimeError("mcp package required")

    server = Server("spector-media-index")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="list_media_probes",
                description="List all media files discovered during extension probing.",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_media_by_doc",
                description="Get media files associated with a specific base URL.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "base_url": {"type": "string"},
                    },
                    "required": ["base_url"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]):
        probes = _load_probes()

        if name == "list_media_probes":
            all_found = []
            for p in probes:
                for url in p.get("found_urls", []):
                    all_found.append(f"{url} (from {p['base_url']})")
            return [TextContent(type="text", text="\n".join(all_found) or "No media found.")]

        if name == "get_media_by_doc":
            base = arguments["base_url"]
            for p in probes:
                if p.get("base_url") == base:
                    return [TextContent(type="text", text=json.dumps(p, indent=2))]
            return [TextContent(type="text", text=f"No probe results for {base}")]

        raise ValueError(f"Unknown tool: {name}")

    return server


async def main():
    server = create_server()
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

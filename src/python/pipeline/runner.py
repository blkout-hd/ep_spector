"""
SPECTOR Pipeline Runner

CLI entry point that builds the LangGraph graph, attaches a checkpointer,
and executes the full pipeline for a given set of source URLs or a local
document directory.

Usage:
    python -m pipeline.runner --urls https://example.com/doc.pdf
    python -m pipeline.runner --dir ./documents
    python -m pipeline.runner --urls URL1 URL2 --tor --gpu cuda13x
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("spector.runner")
console = Console()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="spector-run",
        description="Run the SPECTOR document analysis pipeline",
    )
    parser.add_argument(
        "--urls", nargs="+", default=[],
        help="One or more source document URLs to ingest"
    )
    parser.add_argument(
        "--dir", dest="doc_dir", default=None,
        help="Local directory containing PDF/text documents"
    )
    parser.add_argument(
        "--tor", action="store_true",
        help="Route media probe requests through Tor"
    )
    parser.add_argument(
        "--gpu", dest="gpu_tier", default="cpu",
        choices=["cpu", "cuda12x", "cuda13x"],
        help="GPU acceleration tier"
    )
    parser.add_argument(
        "--run-id", default=None,
        help="Resume a specific run by ID (uses checkpoint)"
    )
    parser.add_argument(
        "--stream", action="store_true",
        help="Stream intermediate state updates to stdout"
    )
    args = parser.parse_args()

    if not args.urls and not args.doc_dir:
        parser.error("Provide --urls or --dir")

    from .graph import build_graph
    from .checkpointer import get_checkpointer

    run_id = args.run_id or str(uuid.uuid4())
    console.rule(f"[bold cyan]SPECTOR Pipeline — run {run_id}[/bold cyan]")

    checkpointer = get_checkpointer()
    graph = build_graph()

    initial_state = {
        "source_urls": args.urls,
        "doc_dir": args.doc_dir,
        "use_tor": args.tor,
        "gpu_tier": args.gpu_tier,
        "run_id": run_id,
        "documents": [],
        "entities": [],
        "embeddings": [],
        "media_probes": [],
        "errors": [],
        "kg_nodes_written": 0,
        "kg_edges_written": 0,
        "stage": "init",
        "complete": False,
    }

    config = {"configurable": {"thread_id": run_id}}

    try:
        if args.stream:
            for event in graph.stream(initial_state, config=config):
                node, state = next(iter(event.items()))
                console.log(f"[green]{node}[/green] → "
                            f"{len(state.get('documents', []))} docs, "
                            f"{len(state.get('entities', []))} entities")
        else:
            final = graph.invoke(initial_state, config=config)
            console.print("[bold green]✓ Pipeline complete[/bold green]")
            console.print(f"  Documents : {len(final.get('documents', []))}")
            console.print(f"  Entities  : {len(final.get('entities', []))}")
            console.print(f"  Embeddings: {len(final.get('embeddings', []))}")
            console.print(f"  KG nodes  : {final.get('kg_nodes_written', 0)}")
            console.print(f"  KG edges  : {final.get('kg_edges_written', 0)}")
            if final.get("errors"):
                console.print(f"[yellow]  Errors ({len(final['errors'])}):[/yellow]")
                for err in final["errors"][:5]:
                    console.print(f"    - {err}")
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted — checkpoint saved[/yellow]")
        return 130
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

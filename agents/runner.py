"""
SPECTOR Agent Worker entrypoint.
Polls Redis queue and runs the LangGraph pipeline per document.
Queue key: spector:ingest_queue
Result TTL: 24h at spector:result:<file_hash>
"""
from __future__ import annotations

import json
import logging
import os
import time

import redis

from agents.pipeline.graph import build_graph
from agents.pipeline.state import PipelineState
from agents.pipeline.checkpointer import get_checkpointer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("spector.runner")

QUEUE_KEY = "spector:ingest_queue"
RESULT_KEY_PREFIX = "spector:result:"
POLL_TIMEOUT = 2  # seconds


def main() -> None:
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.environ["REDIS_PASSWORD"],
        decode_responses=True,
    )

    checkpointer = get_checkpointer()
    pipeline = build_graph(checkpointer=checkpointer)
    logger.info("Agent worker started. Polling: %s", QUEUE_KEY)

    while True:
        item = r.brpop(QUEUE_KEY, timeout=POLL_TIMEOUT)
        if item is None:
            continue

        _, payload = item
        try:
            job = json.loads(payload)
            source = job.get("source") or job.get("source_url", "")
            if not source:
                logger.warning("Job missing source field: %s", payload[:200])
                continue

            logger.info("Processing: %s", source)

            initial_state: PipelineState = {
                "source": source,
                "doc_id": job.get("doc_id"),
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

            result = pipeline.invoke(initial_state)

            r.setex(
                f"{RESULT_KEY_PREFIX}{result['file_hash']}",
                86400,
                json.dumps(
                    {
                        "file_hash": result["file_hash"],
                        "entity_count": result["entity_count"],
                        "kg_edges": result["kg_edges_written"],
                        "n_clusters": result["n_clusters"],
                        "stages": result["completed_stages"],
                        "error": result.get("error"),
                    }
                ),
            )

            logger.info(
                "Done: %s -- %d entities, %d edges, %d clusters",
                result["file_hash"][:12],
                result["entity_count"],
                result["kg_edges_written"],
                result["n_clusters"],
            )

        except Exception:
            logger.error("Job failed: %s", payload[:100], exc_info=True)
            time.sleep(1)


if __name__ == "__main__":
    main()

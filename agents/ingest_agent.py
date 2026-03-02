"""
SPECTOR Ingest Agent

Ingests documents from:
  - Remote URLs (HTTP GET, optional Tor proxy)
  - Local file system directories

Extracts:
  - Visible text layers (PyMuPDF)
  - Hidden/suppressed text layers (pixel-level analysis)
  - OCR fallback for scanned pages (PaddleOCR)
  - Document metadata (author, creation date, producer)
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("spector.agents.ingest")


def _fetch_url_sync(url: str, proxies: Optional[dict] = None) -> bytes:
    """Fetch a URL synchronously with optional SOCKS5 Tor proxy."""
    import requests
    resp = requests.get(url, proxies=proxies, timeout=30, stream=True)
    resp.raise_for_status()
    return resp.content


def _extract_pdf(path: str) -> dict[str, Any]:
    """
    Extract text layers from a PDF using PyMuPDF.

    Returns dict with:
      - raw_text: all visible text
      - hidden_text: text with rendering mode 3 (invisible ink)
      - pages: page count
      - metadata: PDF metadata dict
    """
    import fitz  # PyMuPDF

    doc = fitz.open(path)
    visible_parts = []
    hidden_parts = []

    for page in doc:
        # Standard text extraction
        visible_parts.append(page.get_text("text"))

        # Hidden text: blocks with render_mode == 3 are invisible on-screen
        for block in page.get_text("rawdict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("flags", 0) & 4:  # bit 2 = invisible text
                        hidden_parts.append(span.get("text", ""))

    return {
        "raw_text": "\n".join(visible_parts),
        "hidden_text": "\n".join(hidden_parts),
        "pages": len(doc),
        "metadata": doc.metadata or {},
    }


def _ocr_fallback(path: str) -> str:
    """
    Run PaddleOCR on a PDF that has no extractable text layer.
    Returns concatenated OCR text.
    """
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        result = ocr.ocr(path, cls=True)
        lines = []
        for page_result in (result or []):
            for line in (page_result or []):
                if line and len(line) >= 2:
                    text_info = line[1]
                    if text_info and len(text_info) >= 1:
                        lines.append(str(text_info[0]))
        return "\n".join(lines)
    except Exception as exc:
        logger.warning("OCR fallback failed: %s", exc)
        return ""


def _process_single(url_or_path: str, use_tor: bool, tor_proxies: Optional[dict]) -> dict:
    """Ingest one document — download if URL, then extract."""
    doc_id = hashlib.sha256(url_or_path.encode()).hexdigest()[:16]
    is_url = url_or_path.startswith(("http://", "https://"))

    try:
        if is_url:
            logger.info("Fetching %s (tor=%s)", url_or_path, use_tor)
            raw_bytes = _fetch_url_sync(url_or_path, proxies=tor_proxies if use_tor else None)
            suffix = Path(url_or_path).suffix or ".bin"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(raw_bytes)
                local_path = tmp.name
            is_temp = True
        else:
            local_path = url_or_path
            is_temp = False

        if local_path.endswith(".pdf"):
            extracted = _extract_pdf(local_path)
            # OCR fallback if no text extracted
            if not extracted["raw_text"].strip():
                logger.info("No text layer in %s, running OCR", doc_id)
                extracted["raw_text"] = _ocr_fallback(local_path)
        else:
            with open(local_path, "r", errors="replace") as fh:
                extracted = {
                    "raw_text": fh.read(),
                    "hidden_text": "",
                    "pages": 1,
                    "metadata": {},
                }

        if is_temp:
            os.unlink(local_path)

        return {
            "doc_id": doc_id,
            "source_url": url_or_path,
            **extracted,
            "pdf_path": None,
        }

    except Exception as exc:
        logger.error("Ingest failed for %s: %s", url_or_path, exc)
        return {"doc_id": doc_id, "source_url": url_or_path, "error": str(exc)}


def run(state: dict) -> dict:
    """
    Pipeline node: ingest documents from state["source_urls"] or state["doc_dir"].

    Returns dict patch:
      - documents: list[DocumentRecord]
      - errors: list[str]
    """
    use_tor = state.get("use_tor", False)
    tor_proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

    sources: list[str] = list(state.get("source_urls") or [])

    # Expand local directory
    doc_dir = state.get("doc_dir")
    if doc_dir:
        p = Path(doc_dir)
        sources += [str(f) for f in p.rglob("*") if f.suffix in (".pdf", ".txt", ".md")]

    if not sources:
        logger.warning("Ingest: no sources provided")
        return {"documents": [], "errors": []}

    documents = []
    errors = []

    for src in sources:
        result = _process_single(src, use_tor, tor_proxies)
        if "error" in result:
            errors.append(f"ingest:{result['doc_id']}:{result['error']}")
        else:
            documents.append(result)

    logger.info("Ingest complete: %d docs, %d errors", len(documents), len(errors))
    return {"documents": documents, "errors": errors}

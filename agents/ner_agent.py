"""
SPECTOR NER Agent

Named Entity Recognition using a two-pass approach:
  1. spaCy transformer model (fast, high-precision for standard types)
  2. GLiNER zero-shot NER (catches domain-specific entities:
     e.g. case numbers, flight registrations, financial accounts)

Results are merged and deduplicated by span.
"""
from __future__ import annotations

import logging
import hashlib
from typing import Any

logger = logging.getLogger("spector.agents.ner")

_SPACY_MODEL = "en_core_web_trf"  # falls back to en_core_web_sm if trf not installed
_GLINER_MODEL = "urchade/gliner_medium-v2.1"
_GLINER_LABELS = [
    "person", "organization", "location", "date", "case_number",
    "aircraft_registration", "financial_account", "vessel", "phone",
    "email", "social_security_number", "address",
]

_nlp = None
_gliner = None


def _get_spacy():
    global _nlp
    if _nlp is None:
        import spacy
        try:
            _nlp = spacy.load(_SPACY_MODEL)
        except OSError:
            logger.warning("%s not found, falling back to en_core_web_sm", _SPACY_MODEL)
            try:
                _nlp = spacy.load("en_core_web_sm")
            except OSError:
                import subprocess, sys
                subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
                _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_gliner():
    global _gliner
    if _gliner is None:
        try:
            from gliner import GLiNER
            _gliner = GLiNER.from_pretrained(_GLINER_MODEL)
        except Exception as exc:
            logger.warning("GLiNER unavailable: %s", exc)
    return _gliner


def _extract_spacy(text: str, doc_id: str) -> list[dict]:
    nlp = _get_spacy()
    doc = nlp(text[:100_000])  # spaCy 100k char limit
    entities = []
    for ent in doc.ents:
        entities.append({
            "entity_id": hashlib.sha256(f"{doc_id}{ent.start_char}{ent.text}".encode()).hexdigest()[:12],
            "label": ent.label_,
            "text": ent.text,
            "doc_id": doc_id,
            "confidence": 1.0,  # spaCy doesn't expose span confidence directly
            "span_start": ent.start_char,
            "span_end": ent.end_char,
        })
    return entities


def _extract_gliner(text: str, doc_id: str) -> list[dict]:
    gliner = _get_gliner()
    if gliner is None:
        return []
    try:
        results = gliner.predict_entities(text[:10_000], _GLINER_LABELS, threshold=0.4)
        entities = []
        for r in results:
            entities.append({
                "entity_id": hashlib.sha256(
                    f"{doc_id}g{r.get('start', 0)}{r.get('text', '')}".encode()
                ).hexdigest()[:12],
                "label": r.get("label", "UNKNOWN").upper(),
                "text": r.get("text", ""),
                "doc_id": doc_id,
                "confidence": float(r.get("score", 0.0)),
                "span_start": r.get("start", 0),
                "span_end": r.get("end", 0),
            })
        return entities
    except Exception as exc:
        logger.warning("GLiNER extraction failed for %s: %s", doc_id, exc)
        return []


def _deduplicate(entities: list[dict]) -> list[dict]:
    """Remove overlapping spans, keeping highest confidence."""
    seen_spans: dict[tuple, dict] = {}
    for ent in entities:
        key = (ent["doc_id"], ent["span_start"], ent["span_end"])
        if key not in seen_spans or ent["confidence"] > seen_spans[key]["confidence"]:
            seen_spans[key] = ent
    return list(seen_spans.values())


def run(state: dict) -> dict:
    """
    Pipeline node: run NER on documents in state["documents"].

    Returns dict patch:
      - entities: list[EntityRecord]
      - errors: list[str]
    """
    docs = state.get("documents", [])
    all_entities = []
    errors = []

    for doc in docs:
        doc_id = doc.get("doc_id", "unknown")
        text = doc.get("raw_text", "")
        if not text.strip():
            continue
        try:
            spacy_ents = _extract_spacy(text, doc_id)
            gliner_ents = _extract_gliner(text, doc_id)
            merged = _deduplicate(spacy_ents + gliner_ents)
            all_entities.extend(merged)
            logger.info("NER %s: %d entities", doc_id, len(merged))
        except Exception as exc:
            logger.error("NER failed for %s: %s", doc_id, exc)
            errors.append(f"ner:{doc_id}:{exc}")

    return {"entities": all_entities, "errors": errors}

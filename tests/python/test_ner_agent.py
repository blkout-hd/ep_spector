"""Tests for NERAgent."""
from agents.ner_agent import Entity, NERAgent


def test_spacy_extracts_persons(sample_pdf_text):
    agent = NERAgent(use_gliner=False)
    entities = agent.extract(sample_pdf_text)
    names = [e.normalized for e in entities if e.label == "PERSON"]
    assert any("Epstein" in n for n in names), f"Expected Epstein in {names}"


def test_empty_text_returns_empty():
    agent = NERAgent(use_gliner=False)
    assert agent.extract("") == []
    assert agent.extract("   ") == []


def test_deduplication():
    agent = NERAgent(use_gliner=False)
    text = "John Smith met John Smith again. John Smith left."
    entities = agent.extract(text)
    john_smiths = [e for e in entities if "John Smith" in e.text]
    assert len(john_smiths) <= 1, "Duplicate entities not resolved"


def test_entity_normalization():
    ent = Entity(text="jeffrey epstein", label="PERSON", start=0, end=15)
    assert ent.normalized == "Jeffrey Epstein"

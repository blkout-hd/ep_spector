"""Tests for IngestAgent."""
from agents.ingest_agent import ExtractedDocument, IngestAgent


def test_hash_file_deterministic(tmp_path):
    agent = IngestAgent(ocr_enabled=False)
    f = tmp_path / "test.bin"
    f.write_bytes(b"hello spector")
    h1 = agent._hash_file(str(f))
    h2 = agent._hash_file(str(f))
    assert len(h1) == 64
    assert h1 == h2


def test_extract_returns_none_on_bad_path():
    agent = IngestAgent(ocr_enabled=False)
    result = agent.extract("/nonexistent/path/doc.pdf")
    assert result is None


def test_extracted_document_full_text():
    doc = ExtractedDocument(
        file_hash="abc123",
        source_path="/tmp/test.pdf",
        page_count=2,
        visible_text="Hello World",
        hidden_text="Hidden Content",
        ocr_text="OCR Text",
        has_hidden_text=True,
    )
    full = doc.full_text
    assert "Hello World" in full
    assert "Hidden Content" in full
    assert "OCR Text" in full


def test_extracted_document_no_hidden():
    doc = ExtractedDocument(
        file_hash="def456",
        source_path="/tmp/clean.pdf",
        page_count=1,
        visible_text="Clean document",
        hidden_text="",
        ocr_text="",
        has_hidden_text=False,
    )
    assert doc.full_text == "Clean document"

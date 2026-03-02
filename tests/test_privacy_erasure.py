"""
tests/test_privacy_erasure.py

Comprehensive tests for GDPR/CCPA erasure logic and endpoint.

Test classes:
- TestEraseHelper      : unit-tests _erase_entities_and_documents() directly
- TestEraseEndpoint    : HTTP-level tests via DRF APIClient

All tests use pytest-django with an in-memory SQLite test database.
If Django is not configured they are auto-skipped.
"""
from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Attempt Django setup; skip entire module cleanly if unavailable
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.django_db

try:
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spector_django.settings")
    import django
    django.setup()
    _DJANGO_AVAILABLE = True
except Exception:
    _DJANGO_AVAILABLE = False

if not _DJANGO_AVAILABLE:
    pytestmark = pytest.mark.skip("Django not configured in test env")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def doc_with_identifier(db):
    """A Document whose raw_text contains a known identifier."""
    from spector_django.apps.documents.models import Document
    return Document.objects.create(
        title="Identifier Doc",
        file_hash="aabbccdd" * 8,
        raw_text="Jane Doe signed the contract on 2023-01-01.",
        status=Document.Status.COMPLETE,
    )


@pytest.fixture
def entity_jane(db):
    """An Entity record for 'Jane Doe'."""
    from spector_django.apps.entities.models import Entity
    return Entity.objects.create(
        text="Jane Doe",
        normalized="jane doe",
        label="PERSON",
        confidence=0.99,
    )


@pytest.fixture
def entity_other(db):
    """An unrelated Entity that must NOT be deleted during erasure."""
    from spector_django.apps.entities.models import Entity
    return Entity.objects.create(
        text="Acme Corp",
        normalized="acme corp",
        label="ORG",
        confidence=0.95,
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


# ---------------------------------------------------------------------------
# Unit tests: _erase_entities_and_documents helper
# ---------------------------------------------------------------------------

class TestEraseHelper:
    def test_deletes_matching_entity_by_normalized(self, db, entity_jane, entity_other):
        """Entities matching identifier (case-insensitive) are deleted."""
        from spector_django.apps.entities.models import Entity
        from spector_django.apps.privacy.views import _erase_entities_and_documents

        deleted, _ = _erase_entities_and_documents("Jane Doe")

        assert deleted == 1
        assert not Entity.objects.filter(normalized="jane doe").exists()
        # Unrelated entity survives
        assert Entity.objects.filter(normalized="acme corp").exists()

    def test_deletes_entity_matching_by_text_substring(self, db):
        """Entities where `text` contains the identifier substring are deleted."""
        from spector_django.apps.entities.models import Entity
        from spector_django.apps.privacy.views import _erase_entities_and_documents

        Entity.objects.create(
            text="Dr. Jane Doe PhD",
            normalized="dr jane doe phd",
            label="PERSON",
            confidence=0.90,
        )
        deleted, _ = _erase_entities_and_documents("Jane Doe")
        assert deleted >= 1
        assert not Entity.objects.filter(text__icontains="Jane Doe").exists()

    def test_marks_document_with_erased_identifier(self, db, doc_with_identifier):
        """Documents containing identifier text get metadata updated."""
        from spector_django.apps.documents.models import Document
        from spector_django.apps.privacy.views import _erase_entities_and_documents

        _, docs_marked = _erase_entities_and_documents("Jane Doe")

        assert docs_marked == 1
        doc = Document.objects.get(pk=doc_with_identifier.pk)
        assert "Jane Doe" in doc.metadata.get("erased_identifiers", [])

    def test_document_not_hard_deleted(self, db, doc_with_identifier):
        """Documents are soft-marked, not deleted."""
        from spector_django.apps.documents.models import Document
        from spector_django.apps.privacy.views import _erase_entities_and_documents

        _erase_entities_and_documents("Jane Doe")
        assert Document.objects.filter(pk=doc_with_identifier.pk).exists()

    def test_idempotent_document_marking(self, db, doc_with_identifier):
        """Running erasure twice must not duplicate the erased_identifiers entry."""
        from spector_django.apps.documents.models import Document
        from spector_django.apps.privacy.views import _erase_entities_and_documents

        _erase_entities_and_documents("Jane Doe")
        _, docs_second = _erase_entities_and_documents("Jane Doe")

        doc = Document.objects.get(pk=doc_with_identifier.pk)
        identifiers = doc.metadata.get("erased_identifiers", [])
        assert identifiers.count("Jane Doe") == 1
        assert docs_second == 0  # already marked; no new marks

    def test_no_match_returns_zeros(self, db):
        """When no entities or documents match, both counts are 0."""
        from spector_django.apps.privacy.views import _erase_entities_and_documents

        deleted, marked = _erase_entities_and_documents("Nobody Nowhere")
        assert deleted == 0
        assert marked == 0

    def test_preserves_existing_metadata_keys(self, db, doc_with_identifier):
        """Pre-existing metadata keys are not clobbered by erasure."""
        from spector_django.apps.documents.models import Document
        from spector_django.apps.privacy.views import _erase_entities_and_documents

        doc_with_identifier.metadata = {"classification": "public"}
        doc_with_identifier.save(update_fields=["metadata"])

        _erase_entities_and_documents("Jane Doe")

        doc = Document.objects.get(pk=doc_with_identifier.pk)
        assert doc.metadata.get("classification") == "public"
        assert "Jane Doe" in doc.metadata.get("erased_identifiers", [])

    def test_whitespace_stripped_from_identifier(self, db, entity_jane):
        """Leading/trailing whitespace in the identifier is ignored."""
        from spector_django.apps.entities.models import Entity
        from spector_django.apps.privacy.views import _erase_entities_and_documents

        deleted, _ = _erase_entities_and_documents("  Jane Doe  ")
        assert deleted == 1
        assert not Entity.objects.filter(normalized="jane doe").exists()


# ---------------------------------------------------------------------------
# HTTP-level tests: EraseRequestView
# ---------------------------------------------------------------------------

class TestEraseEndpoint:
    def test_missing_identifier_returns_400(self, db, api_client):
        """POST without identifier field returns HTTP 400."""
        resp = api_client.post(
            "/api/privacy/erase/",
            data={},
            format="json",
        )
        assert resp.status_code == 400
        assert "identifier" in resp.data.get("error", "")

    def test_blank_identifier_returns_400(self, db, api_client):
        """POST with blank identifier returns HTTP 400."""
        resp = api_client.post(
            "/api/privacy/erase/",
            data={"identifier": "   "},
            format="json",
        )
        assert resp.status_code == 400

    def test_valid_request_returns_202(self, db, api_client):
        """A valid erasure request returns HTTP 202."""
        resp = api_client.post(
            "/api/privacy/erase/",
            data={"identifier": "Nobody Nowhere"},
            format="json",
        )
        assert resp.status_code == 202

    def test_response_contains_summary(self, db, api_client):
        """202 response body contains status + summary keys."""
        resp = api_client.post(
            "/api/privacy/erase/",
            data={"identifier": "Test Person"},
            format="json",
        )
        assert resp.status_code == 202
        body = resp.data
        assert body["status"] == "queued"
        assert "summary" in body
        assert "entities_deleted" in body["summary"]
        assert "documents_marked" in body["summary"]

    def test_endpoint_deletes_entity_and_marks_doc(
        self, db, api_client, entity_jane, doc_with_identifier
    ):
        """End-to-end: entity deleted + document marked via HTTP call."""
        from spector_django.apps.documents.models import Document
        from spector_django.apps.entities.models import Entity

        resp = api_client.post(
            "/api/privacy/erase/",
            data={"identifier": "Jane Doe"},
            format="json",
        )
        assert resp.status_code == 202
        assert resp.data["summary"]["entities_deleted"] == 1
        assert resp.data["summary"]["documents_marked"] == 1

        assert not Entity.objects.filter(normalized="jane doe").exists()
        doc = Document.objects.get(pk=doc_with_identifier.pk)
        assert "Jane Doe" in doc.metadata.get("erased_identifiers", [])

    def test_external_stores_field_present(self, db, api_client):
        """Summary must include external_stores field (documenting pending work)."""
        resp = api_client.post(
            "/api/privacy/erase/",
            data={"identifier": "Ghost User"},
            format="json",
        )
        assert "external_stores" in resp.data.get("summary", {})

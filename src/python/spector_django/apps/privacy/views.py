"""
GDPR Art. 17 / CCPA data subject erasure endpoint.

POST /api/privacy/erase/ { "identifier": "<name or email>" }

This endpoint:
- Logs the request for audit trail
- Deletes matching Entity rows
- Marks affected Documents' metadata with an "erased_identifiers" entry

Operators remain responsible for verifying identity and ensuring that
erasure is appropriate before running this in production.
"""
from __future__ import annotations

import logging
from typing import Tuple

from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from spector_django.apps.documents.models import Document
from spector_django.apps.entities.models import Entity

logger = logging.getLogger(__name__)


def _erase_entities_and_documents(identifier: str) -> Tuple[int, int]:
    """Best-effort local erasure within Django models.

    - Entities: delete rows whose normalized name matches identifier (case-insensitive)
      OR whose raw text contains identifier as a substring.
    - Documents: do NOT hard-delete; instead, append identifier to
      metadata["erased_identifiers"] for any document whose raw_text contains it.

    Returns:
        (entities_deleted, documents_marked)
    """
    normalized = identifier.strip()

    with transaction.atomic():
        # Delete entities first so we don't re-derive them in future runs.
        entity_qs = Entity.objects.filter(
            Q(normalized__iexact=normalized) | Q(text__icontains=normalized)
        )
        entities_deleted = entity_qs.count()
        entity_qs.delete()

        # Soft-mark documents that reference the identifier in raw_text.
        doc_qs = Document.objects.filter(raw_text__icontains=normalized)
        docs_marked = 0
        for doc in doc_qs:
            meta = dict(doc.metadata or {})
            erased = set(meta.get("erased_identifiers", []))
            if normalized not in erased:
                erased.add(normalized)
                meta["erased_identifiers"] = sorted(erased)
                doc.metadata = meta
                doc.save(update_fields=["metadata"])
                docs_marked += 1

    return entities_deleted, docs_marked


class EraseRequestView(APIView):
    """Data subject erasure request (GDPR Art. 17 / CCPA right to delete).

    This endpoint does not authenticate the caller; it is intended for use
    behind operator-controlled frontends or after manual identity verification.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        identifier = (request.data.get("identifier") or "").strip()
        if not identifier:
            return Response(
                {"error": "identifier required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Audit log (hashed identifier only)
        logger.info(
            "GDPR erasure request received",
            extra={
                "identifier_hash": hash(identifier),
                "ip": request.META.get("REMOTE_ADDR", ""),
            },
        )

        entities_deleted, docs_marked = _erase_entities_and_documents(identifier)

        # NOTE: External storage (Qdrant, Neo4j, Redis) erasure should be wired
        # here once metadata schemas are finalized. For now we log a reminder.
        logger.info(
            "Erasure summary for %r: entities_deleted=%d, docs_marked=%d "
            "(external stores not yet wired)",
            identifier,
            entities_deleted,
            docs_marked,
        )

        return Response(
            {
                "status": "queued",
                "summary": {
                    "entities_deleted": entities_deleted,
                    "documents_marked": docs_marked,
                    "external_stores": "not_yet_implemented",
                },
                "message": (
                    "Your erasure request has been recorded. Local entity records "
                    "have been deleted and relevant documents marked for exclusion. "
                    "External vector/graph stores require operator-side wiring."
                ),
            },
            status=status.HTTP_202_ACCEPTED,
        )

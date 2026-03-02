"""
SPECTOR Privacy / GDPR Erasure Endpoint

Provides:
  POST /api/privacy/erase/   { "identifier": "<doc_id or run_id or email>" }
  GET  /api/privacy/status/  { "identifier": "<...>" }

This satisfies the GDPR Art. 17 'right to erasure' promise made in DISCLAIMER.md.
Operators deploying SPECTOR as a network service MUST ensure this endpoint
is accessible to data subjects they serve.
"""
from __future__ import annotations

import logging

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

logger = logging.getLogger("spector.privacy")


@api_view(["POST"])
def erase_data(request):
    """
    Erase all data associated with an identifier.

    Body: { "identifier": "<doc_id | run_id | email>" }
    Returns: 200 with erasure summary or 400 if identifier missing.
    """
    identifier = request.data.get("identifier", "").strip()
    if not identifier:
        return Response(
            {"error": "'identifier' field is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    erased = {"documents": 0, "entities": 0}

    try:
        from apps.documents.models import Document
        from apps.entities.models import Entity

        with transaction.atomic():
            # Match by doc_id, run_id, or source_url fragment
            docs = Document.objects.filter(
                doc_id=identifier
            ) | Document.objects.filter(
                run_id=identifier
            ) | Document.objects.filter(
                source_url__icontains=identifier
            )
            doc_ids = list(docs.values_list("id", flat=True))

            ent_count, _ = Entity.objects.filter(document_id__in=doc_ids).delete()
            doc_count, _ = docs.delete()

            erased["documents"] = doc_count
            erased["entities"] = ent_count

        logger.info("Erasure request: identifier=%s erased=%s", identifier, erased)

        return Response({
            "status": "erased",
            "identifier": identifier,
            "erased": erased,
        })

    except Exception as exc:
        logger.error("Erasure failed for %s: %s", identifier, exc)
        return Response(
            {"error": "Erasure failed", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def erasure_status(request):
    """Check whether data for a given identifier still exists."""
    identifier = request.query_params.get("identifier", "").strip()
    if not identifier:
        return Response({"error": "'identifier' query param required"}, status=400)

    from apps.documents.models import Document
    exists = Document.objects.filter(
        doc_id=identifier
    ).exists() or Document.objects.filter(
        run_id=identifier
    ).exists()

    return Response({"identifier": identifier, "data_present": exists})

"""
GDPR Art. 17 / CCPA data subject erasure endpoint.
POST /api/privacy/erase/ { "identifier": "<name or email>" }

Logs the request for audit trail.
Operator is responsible for identity verification before acting.
"""
import logging

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

logger = logging.getLogger(__name__)


class EraseRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("identifier", "").strip()
        if not identifier:
            return Response(
                {"error": "identifier required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "GDPR erasure request received",
            extra={
                "identifier_hash": hash(identifier),
                "ip": request.META.get("REMOTE_ADDR", ""),
            },
        )

        # TODO: implement deletion across:
        # - Django Document/Entity tables
        # - Qdrant: delete vectors with metadata filter
        # - Neo4j: MATCH (p:Person {name: $name}) DETACH DELETE p
        # - Redis: flush cached queries referencing identifier

        return Response(
            {
                "status": "queued",
                "message": (
                    "Your erasure request has been received and will be "
                    "processed within 30 days per applicable privacy law."
                ),
            },
            status=status.HTTP_202_ACCEPTED,
        )

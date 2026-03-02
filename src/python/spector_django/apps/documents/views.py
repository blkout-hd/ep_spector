"""Document REST API views."""
import hashlib

from rest_framework import generics, status
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .serializers import DocumentSerializer


class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filterset_fields = ["status", "language", "has_hidden_text"]
    search_fields = ["title", "source_url"]
    ordering_fields = ["created_at", "suppression_score", "redaction_score"]


class DocumentDetailView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentStatusView(APIView):
    def get(self, request, pk):
        try:
            doc = Document.objects.get(pk=pk)
            return Response({
                "id": str(doc.id),
                "status": doc.status,
                "error": doc.error_message or None,
            })
        except Document.DoesNotExist:
            return Response(
                {"error": "not found"}, status=status.HTTP_404_NOT_FOUND
            )


class IngestView(APIView):
    """
    Submit a document URL or file for ingestion.
    POST { "source_url": "https://..." } or multipart PDF upload.
    Enqueues document for processing by the agent worker via Redis.
    """

    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request):
        source_url = request.data.get("source_url", "")
        uploaded_file = request.FILES.get("file")

        if not source_url and not uploaded_file:
            return Response(
                {"error": "Provide source_url or file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_file:
            file_bytes = uploaded_file.read()
            file_hash = hashlib.sha256(file_bytes).hexdigest()
        else:
            file_hash = hashlib.sha256(source_url.encode()).hexdigest()

        doc, created = Document.objects.get_or_create(
            file_hash=file_hash,
            defaults={
                "source_url": source_url,
                "title": (
                    source_url.split("/")[-1]
                    if source_url
                    else uploaded_file.name
                ),
                "status": Document.Status.PENDING,
            },
        )

        if not created:
            return Response(
                {"id": str(doc.id), "status": doc.status, "duplicate": True},
                status=status.HTTP_200_OK,
            )

        # Enqueue to Redis job queue for agent worker
        try:
            import json
            import os
            import redis as redis_lib
            r = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "redis"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.environ["REDIS_PASSWORD"],
                decode_responses=True,
            )
            r.lpush(
                "spector:ingest_queue",
                json.dumps({"source_url": source_url, "doc_id": str(doc.id)}),
            )
        except Exception:
            pass  # Worker will pick up on next poll cycle

        return Response(
            {"id": str(doc.id), "status": doc.status, "duplicate": False},
            status=status.HTTP_202_ACCEPTED,
        )

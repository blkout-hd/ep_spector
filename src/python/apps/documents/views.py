"""Document API views."""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["doc_id", "source_url", "run_id"]
    ordering_fields = ["ingested_at", "suppression_score", "pages"]

    @action(detail=False, methods=["get"])
    def high_suppression(self, request):
        """Return documents with suppression_score > 0.3."""
        threshold = float(request.query_params.get("threshold", 0.3))
        qs = self.get_queryset().filter(suppression_score__gt=threshold)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

from rest_framework import generics
from .models import Entity
from .serializers import EntitySerializer


class EntityListView(generics.ListAPIView):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    filterset_fields = ["label", "source_model"]
    search_fields = ["normalized", "text"]
    ordering_fields = ["confidence", "created_at"]


class EntityDetailView(generics.RetrieveAPIView):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from rest_framework import serializers as drf_serializers
from .models import Entity


class EntitySerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["entity_id", "label", "text", "confidence", "document_id", "created_at"]


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer


router = DefaultRouter()
router.register(r"", EntityViewSet, basename="entity")
urlpatterns = router.urls

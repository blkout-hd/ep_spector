from rest_framework import serializers
from .models import Entity


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = [
            "id", "text", "normalized", "label",
            "confidence", "source_model", "neo4j_id",
            "source_documents", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

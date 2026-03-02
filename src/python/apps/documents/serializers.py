"""DRF serializers for Document."""
from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "doc_id", "source_url", "pages",
            "suppression_score", "ingested_at", "run_id",
        ]
        read_only_fields = ["ingested_at"]

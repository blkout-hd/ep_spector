"""Document serializers."""
from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "source_url",
            "file_hash",
            "page_count",
            "has_hidden_text",
            "redaction_score",
            "suppression_score",
            "ocr_applied",
            "language",
            "status",
            "error_message",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "file_hash", "created_at", "updated_at"]

"""
Document model -- tracks ingested PDFs and their analysis state.
Fields map directly to the KG_SCHEMA.md Document node definition.
"""
import uuid

from django.db import models


class Document(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=512, blank=True)
    source_url = models.URLField(max_length=2048, blank=True)
    file_hash = models.CharField(max_length=64, unique=True, db_index=True)
    page_count = models.PositiveIntegerField(default=0)
    has_hidden_text = models.BooleanField(default=False)
    redaction_score = models.FloatField(default=0.0)
    suppression_score = models.FloatField(default=0.0)  # L2 embedding delta norm
    ocr_applied = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default="en")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    error_message = models.TextField(blank=True)
    raw_text = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["suppression_score"]),
        ]

    def __str__(self) -> str:
        return f"{self.title or self.file_hash[:12]} ({self.status})"

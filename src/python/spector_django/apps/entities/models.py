"""
Entity model -- mirrors Person/Organization nodes from KG_SCHEMA.md.
Stores extracted entities for Django-side querying and export.
"""
import uuid

from django.db import models


class Entity(models.Model):
    class EntityType(models.TextChoices):
        PERSON = "PERSON", "Person"
        ORGANIZATION = "ORG", "Organization"
        LOCATION = "LOCATION", "Location"
        EVENT = "EVENT", "Event"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=512, db_index=True)
    normalized = models.CharField(max_length=512, db_index=True)
    label = models.CharField(
        max_length=20, choices=EntityType.choices, default=EntityType.OTHER
    )
    confidence = models.FloatField(default=1.0)
    source_model = models.CharField(max_length=50, default="spacy")
    neo4j_id = models.CharField(max_length=128, blank=True)
    source_documents = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-confidence", "normalized"]
        indexes = [
            models.Index(fields=["label", "confidence"]),
        ]
        unique_together = [("normalized", "label")]

    def __str__(self) -> str:
        return f"{self.normalized} ({self.label})"

"""Entity model — mirrors NER agent EntityRecord."""
from django.db import models
from apps.documents.models import Document


class Entity(models.Model):
    entity_id = models.CharField(max_length=64, unique=True, db_index=True)
    label = models.CharField(max_length=64, db_index=True)
    text = models.TextField()
    confidence = models.FloatField(default=0.0)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE,
        related_name="entities", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-confidence"]
        verbose_name_plural = "entities"

    def __str__(self):
        return f"{self.label}: {self.text[:50]}"

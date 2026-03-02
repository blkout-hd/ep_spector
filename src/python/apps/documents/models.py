"""Document model — mirrors the ingest agent DocumentRecord."""
from django.db import models


class Document(models.Model):
    doc_id = models.CharField(max_length=64, unique=True, db_index=True)
    source_url = models.URLField(max_length=2048, blank=True)
    raw_text = models.TextField(blank=True)
    hidden_text = models.TextField(blank=True)
    pages = models.IntegerField(default=0)
    suppression_score = models.FloatField(null=True, blank=True)
    ingested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    run_id = models.CharField(max_length=64, blank=True, db_index=True)

    class Meta:
        ordering = ["-ingested_at"]

    def __str__(self):
        return f"Document({self.doc_id})"

from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                    ),
                ),
                ("title", models.CharField(max_length=512, blank=True)),
                (
                    "source_url",
                    models.URLField(max_length=2048, blank=True),
                ),
                (
                    "file_hash",
                    models.CharField(
                        max_length=64,
                        unique=True,
                        db_index=True,
                    ),
                ),
                ("page_count", models.PositiveIntegerField(default=0)),
                ("has_hidden_text", models.BooleanField(default=False)),
                ("redaction_score", models.FloatField(default=0.0)),
                ("suppression_score", models.FloatField(default=0.0)),
                ("ocr_applied", models.BooleanField(default=False)),
                ("language", models.CharField(max_length=10, default="en")),
                (
                    "status",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("complete", "Complete"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        db_index=True,
                    ),
                ),
                ("error_message", models.TextField(blank=True)),
                ("raw_text", models.TextField(blank=True)),
                ("metadata", models.JSONField(default=dict)),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["status", "created_at"]),
                    models.Index(fields=["suppression_score"]),
                ],
            },
        )
    ]

from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Entity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                    ),
                ),
                (
                    "text",
                    models.CharField(max_length=512, db_index=True),
                ),
                (
                    "normalized",
                    models.CharField(max_length=512, db_index=True),
                ),
                (
                    "label",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("PERSON", "Person"),
                            ("ORG", "Organization"),
                            ("LOCATION", "Location"),
                            ("EVENT", "Event"),
                            ("OTHER", "Other"),
                        ],
                        default="OTHER",
                    ),
                ),
                ("confidence", models.FloatField(default=1.0)),
                (
                    "source_model",
                    models.CharField(max_length=50, default="spacy"),
                ),
                ("neo4j_id", models.CharField(max_length=128, blank=True)),
                ("source_documents", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-confidence", "normalized"],
                "indexes": [
                    models.Index(fields=["label", "confidence"]),
                ],
                "unique_together": {("normalized", "label")},
            },
        )
    ]

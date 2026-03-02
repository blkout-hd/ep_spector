"""Document API routes."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.DocumentListView.as_view(), name="document-list"),
    path("<uuid:pk>/", views.DocumentDetailView.as_view(), name="document-detail"),
    path("ingest/", views.IngestView.as_view(), name="document-ingest"),
    path("status/<uuid:pk>/", views.DocumentStatusView.as_view(), name="document-status"),
]

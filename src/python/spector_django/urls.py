"""SPECTOR URL Configuration."""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok", "service": "spector-django"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/documents/", include("spector_django.apps.documents.urls")),
    path("api/entities/", include("spector_django.apps.entities.urls")),
    path("api/privacy/", include("spector_django.apps.privacy.urls")),
    path("api-auth/", include("rest_framework.urls")),
]

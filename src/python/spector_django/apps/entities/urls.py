from django.urls import path
from . import views

urlpatterns = [
    path("", views.EntityListView.as_view(), name="entity-list"),
    path("<uuid:pk>/", views.EntityDetailView.as_view(), name="entity-detail"),
]

from django.urls import path
from .views import erase_data, erasure_status

urlpatterns = [
    path("erase/", erase_data, name="privacy-erase"),
    path("status/", erasure_status, name="privacy-status"),
]

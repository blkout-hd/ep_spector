from django.urls import path
from .views import EraseRequestView

urlpatterns = [
    path("erase/", EraseRequestView.as_view(), name="privacy-erase"),
]

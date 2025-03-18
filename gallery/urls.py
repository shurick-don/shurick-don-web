from django.urls import path
from .views import *


urlpatterns = [
    path("", GalleryView.as_view(), name="gallery"),
]

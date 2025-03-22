from django.urls import path
from .views import *

app_name = "gallery"

urlpatterns = [
    path("", GalleryView.as_view(), name="gallery"),
    path("category/<int:pk>/", get_category, name="category"),
]

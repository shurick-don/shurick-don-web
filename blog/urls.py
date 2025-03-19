from django.urls import path

from .views import *

urlpatterns = [
    path("", ArticlesView.as_view(), name="blog"),
    path(
        "category/<str:slug>/",
        ArticlesByCategoryView.as_view(),
        name="articles_by_category",
    ),
    path("articles/<str:slug>/", ArticleView.as_view(), name="article"),
]

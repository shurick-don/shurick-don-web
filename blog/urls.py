from django.urls import path

from .views import *

urlpatterns = [
    path("", ArticlesView.as_view(), name="blog"),
    path("articles/create/", ArticleCreateView.as_view(), name="article_create"),
    path(
        "category/<str:slug>/",
        ArticlesByCategoryView.as_view(),
        name="articles_by_category",
    ),
    path("articles/<str:slug>/", ArticleView.as_view(), name="article"),
    path(
        "articles/<str:slug>/update/",
        ArticleUpdateView.as_view(),
        name="article_update",
    ),
]

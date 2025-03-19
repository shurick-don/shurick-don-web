from django import forms

from .models import Article


class ArticleCreateForm(forms.ModelForm):
    """
    Форма добавления статей на сайте
    """

    class Meta:
        model = Article
        fields = (
            "title",
            "category",
            "short_description",
            "full_description",
            "thumbnail",
            "status",
        )


class ArticleUpdateForm(ArticleCreateForm):
    """
    Форма обновления статьи на сайте
    """

    class Meta:
        model = Article
        fields = ArticleCreateForm.Meta.fields

from django import forms

from .models import Article


class ArticleCreateForm(forms.ModelForm):
    """
    Форма добавления статей на сайте
    """

    class Meta:
        model = Article
        fields = ('title', 'category', 'short_description', 'full_description', 'thumbnail', 'status')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['full_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['full_description'].required = False



class ArticleUpdateForm(ArticleCreateForm):
    """
    Форма обновления статьи на сайте
    """
    class Meta:
        model = Article
        fields = ArticleCreateForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['full_description'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['full_description'].required = False
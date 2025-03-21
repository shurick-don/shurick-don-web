from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from utils import DataMixin
from .models import Article, Category
from .forms import ArticleCreateForm, ArticleUpdateForm


def gallery_post(request):
    posts = Article.objects.all()
    return render(request, "blog/gallery_post.html", {"posts": posts})


# DataMixin - миксин с данными для панели навигации
class ArticlesView(DataMixin, ListView):
    """
    Представление: отображение статей в блоге
    """

    paginate_by = 5  # Настройка пагинации (5 статей на странице)
    model = Article  # Указание модели для ListView
    template_name = (
        "blog/blog.html"  # Путь к шаблону html ("blog(название приложения)/blog.html")
    )
    context_object_name = "articles"  # Название переменной из модели Article (вместо стандартного "object_list")

    def get_queryset(self):
        """
        Переопределение метода get_queryset: получаем qs, возвращаем же qs упорядоченный по дате создания поста
        (от новых к старым), дополнительно отфильтровав по содержимому "поиска"
        """
        # Получение значения по ключу search из request.GET (QueryDict)
        search_query = self.request.GET.get("search", "")
        # Возврат упорядоченного qs + отфильтрованному по совпадению из search_query
        return (
            Article.objects.all()
            .order_by("-time_create")
            .filter(
                Q(title__icontains=search_query)
                | Q(slug__icontains=search_query)
                | Q(full_description__icontains=search_query)
            )
        )

    def get_context_data(self, *args, object_list=None, **kwargs):
        """
        Функция получения контекста
        """
        context = super().get_context_data(
            **kwargs
        )  # Получение словаря с контекстом (в т.ч. навигацией из DataMixin)
        c_def = self.get_mixin_context(
            title="AM | Блог"
        )  # Добавление ключа title в контекст
        return dict(
            list(context.items()) + list(c_def.items())
        )  # Возвращение итогового словаря с контекстом


# DataMixin - миксин с данными для панели навигации
class ArticlesByCategoryView(DataMixin, ListView):
    """
    Представление: отображение статей, сгруппированных по полю "категория"
    """

    paginate_by = 5  # Настройка пагинации (5 статей на странице)
    model = Article  # Указание модели для ListView
    template_name = (
        "blog/blog.html"  # Путь к шаблону html ("blog(название приложения)/blog.html")
    )
    context_object_name = "articles"  # Название переменной из модели Article (вместо стандартного "object_list")

    def get_queryset(self):
        """
        Переопределение метода get_queryset: получаем категорию по определенному slug, после чего фильтруем qs статей по
        категории и возвращаем qs.
        """
        self.category = Category.objects.get(
            slug=self.kwargs["slug"]
        )  # Получение объекта категории по slug
        queryset = Article.objects.all().filter(
            category__slug=self.category.slug
        )  # Фильтр статей по slug категории
        return queryset

    def get_context_data(self, **kwargs):
        """
        Функция получения контекста
        """
        context = super().get_context_data(
            **kwargs
        )  # Получение словаря с контекстом (в т.ч. навигацией из DataMixin)
        c_def = self.get_mixin_context(
            title=f"AM | {self.category.title}"
        )  # Добавление ключа title в контекст
        return dict(
            list(context.items()) + list(c_def.items())
        )  # Возвращение итогового словаря с контекстом


# DataMixin - миксин с данными для панели навигации
class ArticleView(DataMixin, DetailView):
    """
    Представление: отображение отдельной статьи
    """

    model = Article  # Указание модели для DetailView
    template_name = "blog/article.html"  # Путь к шаблону html ("blog(название приложения)/article.html")
    context_object_name = "article"  # Название переменной из модели Article (вместо стандартного "object_list")

    def get_context_data(self, **kwargs):
        """
        Функция получения контекста
        """
        context = super().get_context_data(
            **kwargs
        )  # Получение словаря с контекстом (в т.ч. навигацией из DataMixin)
        c_def = self.get_mixin_context(
            title=f"AM | {self.object.title}"
        )  # Добавление ключа title в контекст
        return dict(
            list(context.items()) + list(c_def.items())
        )  # Возвращение итогового словаря с контекстом


# LoginRequiredMixin - миксин для ограничения доступа неавторизованного пользователя на страницу
# DataMixin - миксин с данными для панели навигации
class ArticleCreateView(LoginRequiredMixin, DataMixin, CreateView):
    """
    Представление: создание статьи на сайте
    """

    form_class = ArticleCreateForm  # Указание класса формы
    template_name = "blog/article_create.html"  # Путь к шаблону html ("blog(название приложения)/article_create.html")
    success_url = reverse_lazy(
        "blog"
    )  # Путь, на который произойдет переадресация при успешной валидации формы

    def get_context_data(self, **kwargs):
        """
        Функция получения контекста
        """
        context = super().get_context_data(
            **kwargs
        )  # Получение словаря с контекстом (в т.ч. навигацией из DataMixin)
        c_def = self.get_mixin_context(
            title="AM | Добавление статьи"
        )  # Добавление ключа title в контекст
        return dict(
            list(context.items()) + list(c_def.items())
        )  # Возвращение итогового словаря с контекстом


# LoginRequiredMixin - миксин для ограничения доступа неавторизованного пользователя на страницу
# DataMixin - миксин с данными для панели навигации
class ArticleUpdateView(LoginRequiredMixin, DataMixin, UpdateView):
    """
    Представление: обновление статьи на сайте
    """

    model = Article  # Указание модели для UpdateView
    form_class = ArticleUpdateForm  # Указание класса формы
    template_name = "blog/article_update.html"  # Путь к шаблону html ("blog(название приложения)/article_update.html")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(
            **kwargs
        )  # Получение словаря с контекстом (в т.ч. навигацией из DataMixin)
        c_def = self.get_mixin_context(
            title=f"Обновление статьи: {self.object.title}"
        )  # Добавление ключа title в контекст
        return dict(
            list(context.items()) + list(c_def.items())
        )  # Возвращение итогового словаря с контекстом

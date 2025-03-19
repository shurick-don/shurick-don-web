from django.shortcuts import render

from django.db.models import Q
from django.views.generic import ListView, DetailView

from .models import Article
from utils import DataMixin

from .models import Article, Category


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

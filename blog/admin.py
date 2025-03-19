from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db import models

from mptt.admin import DraggableMPTTAdmin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    """
    Админ-панель модели категорий
    """

    # отображаемые в админ-панели поля модели
    list_display = (
        "tree_actions",
        "indented_title",
        "id",
        "title",
        "slug",
        "articles_count",
    )
    # поля, которые имеют ссылку на объект модели (по клику на соответсвующее поле -> переход к редактированию)
    list_display_links = ("indented_title", "title", "slug")
    # автоматическое заполнение slug латинскими буквами
    prepopulated_fields = {"slug": ("title",)}

    # поля, которые отображаются в редакторе объекта модели с разбиением по блокам
    fieldsets = (
        ("Основная информация", {"fields": ("title", "slug", "parent")}),
        ("Описание", {"fields": ("description",)}),
    )

    def get_queryset(self, request):
        """
        Метод, определяющий кол-во статей, которые были опубликованы в каждой из категорий
        """
        qs = super().get_queryset(request)

        # Создание нового поля "articles_count" в qs, в который передается сумма статей со статусом = 1 (PUBLISHED)
        qs = qs.annotate(
            articles_count=models.Sum(
                models.Case(
                    models.When(articles__status=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            )
        )

        return qs

    # Декоратор для определения понятного для человека названия метода, которое будет отображаться в админ-панели
    @admin.display(description="Статей в категории")
    def articles_count(self, instance):
        """
        Метод вывода информации из qs, по полю articles_count
        """
        return instance.articles_count


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Админ-панель модели статей
    """

    # Отображаемые в админ-панели поля модели
    list_display = (
        "id",
        "category",
        "title",
        "get_html_thumbnail_75",
        "status",
        "time_create",
        "time_update",
    )
    # Поля, которые имеют ссылку на объект модели (по клику на соответсвующее поле -> переход к редактированию)
    list_display_links = ("id", "title", "get_html_thumbnail_75")
    # Поля, которые можно редактировать из админ-панели (не переходя в редактор самого объекта модели)
    list_editable = ("status",)
    # Пагинация внутри админ-панели (10 объектов на странице)
    list_per_page = 10
    # Добавление "действия" в админ-панели
    actions = ["set_status_published", "set_status_draft"]
    # Поля, для которых осуществляется поиск (т.к. категория - это другая модель, ссылаемся на ее название через "__")
    search_fields = ("category__title", "title", "status")
    # Добавление фильтрации по полям
    list_filter = ("category__title", "status", "time_create", "time_update")

    # Поля, которые отображаются в редакторе объекта модели с разбиением по блокам
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("get_html_thumbnail_150", "thumbnail", "title", "slug")},
        ),
        (
            "Описание",
            {
                "fields": (
                    "category",
                    "short_description",
                    "full_description",
                )
            },
        ),
        ("Публикация", {"fields": ("status",)}),
    )
    # Поля только для чтения
    readonly_fields = ("get_html_thumbnail_150",)
    # Автоматическое заполнение slug латинскими буквами
    prepopulated_fields = {"slug": ("title",)}

    # Декоратор для определения понятного для человека названия метода, которое будет отображаться в админ-панели
    @admin.display(description="Превью")
    def get_html_thumbnail_75(self, instance):
        """
        Метод, возвращающий эскиз фотографии превью (поле thumbnail)
        """
        # Если поле thumbnail объекта модели существует, вернуть html тег img высотой 75px
        if instance.thumbnail:
            return mark_safe(f'<img src="{instance.thumbnail.url}" height=75>')

    # Декоратор для определения понятного для человека названия метода, которое будет отображаться в админ-панели
    @admin.display(description="Превью")
    def get_html_thumbnail_150(self, instance):
        """
        Метод, возвращающий эскиз фотографии превью (поле thumbnail)
        """
        # Если поле thumbnail объекта модели существует, вернуть html тег img высотой 150px
        if instance.thumbnail:
            return mark_safe(f'<img src="{instance.thumbnail.url}" height=150>')

    # Декоратор для определения понятного для человека названия "действия", которое будет отображаться в админ-панели
    @admin.action(description="Опубликовать выбранные записи")
    def set_status_published(self, requset, queryset):
        # Для полученного в request qs обновим поле 'status'
        count = queryset.update(status=Article.Status.PUBLISHED)
        # Вернем сообщение с кол-вом измененных записей
        self.message_user(requset, f"{count} записи(-ей) опубликованы")

    # Декоратор для определения понятного для человека названия "действия", которое будет отображаться в админ-панели
    @admin.action(description="Снять с публикации выбранные записи")
    def set_status_draft(self, requset, queryset):
        # Для полученного в request qs обновим поле 'status'
        count = queryset.update(status=Article.Status.DRAFT)
        # Вернем сообщение с кол-вом измененных записей
        self.message_user(requset, f"{count} записи(-ей) сняты с публикации")

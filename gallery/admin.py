from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Gallery


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    """
    Админ-панель модели галереи
    """

    # Отображаемые в админ-панели поля модели
    list_display = ("id", "get_html_photo_full", "title", "content")
    # Поля, которые имеют ссылку на объект модели (по клику на соответсвующее поле -> переход к редактированию)
    list_display_links = ("id", "get_html_photo_full", "title", "content")
    # Поля, для которых осуществляется поиск
    search_fields = ("title", "content")
    # Поля, которые отображаются в редакторе объекта модели (важно для подгрузки методов отображения эскиза фото)
    fields = ("get_html_photo_full", "title", "content", "photo_full")
    # Поля только для чтения
    readonly_fields = ("get_html_photo_full",)

    def get_html_photo_full(self, object):
        """
        Метод, возвращающий эскиз фотографии (поле photo_full)
        """
        # Если поле photo_full объекта модели существует, вернуть html тег img высотой 75px
        if object.photo_compressed:
            return mark_safe(f'<img src="{object.photo_full.url}" height=75>')

    # Определение понятного названия метода, которое будет отображаться в админ-панели
    get_html_photo_full.short_description = "Миниатюра (HD)"

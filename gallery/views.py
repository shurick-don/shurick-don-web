from django.shortcuts import render
from django.views.generic import ListView

from .models import *
from utils import DataMixin


# DataMixin - миксин с данными для панели навигации
class GalleryView(DataMixin, ListView):
    """
    Представление: отображение галереи
    """

    paginate_by = 9  # Настройка пагинации (9 фото на странице)
    model = Gallery  # Указание модели для ListView
    template_name = "gallery/gallery.html"  # Путь к шаблону html ("<название приложения>/photos.html")
    context_object_name = "photos"  # Название переменной из модели Gallery (вместо стандартного "object_list")

    def get_context_data(self, *args, object_list=None, **kwargs):
        """
        Функция получения контекста
        """
        context = super().get_context_data(
            **kwargs
        )  # Получение словаря с контекстом (в т.ч. навигацией из DataMixin)
        c_def = self.get_mixin_context(
            title="AM | Фото"
        )  # Добавление ключа title в контекст
        return dict(
            list(context.items()) + list(c_def.items())
        )  # Возвращение итогового словаря с контекстом

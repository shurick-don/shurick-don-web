from django.shortcuts import render
from django.views import View

from utils import DataMixin


# DataMixin - миксин с данными для панели навигации
class MainView(DataMixin, View):
    """
    Представление: отображение основной страницы сайта
    """

    def get(self, request):
        """
        Метод, выполняющийся при GET запросе
        """
        context = self.get_mixin_context(
            title="Александр Максименко"
        )  # Добавление ключа title в контекст
        return render(
            request, "main/main.html", context=context
        )  # Рендер шаблона с необходимым контекстом


def pageNotFound(request, exception):
    """
    Обработка ошибки 404
    """
    return render(
        request=request,
        template_name="main/error404.html",
        status=404,
        context={
            "title": "Страница не найдена: 404",  # Передача в контекст заголовка страницы
            "nav": [
                {"title": "На главную", "url_name": "main"}
            ],  # Передача в контекст навигации (только возврат на главную)
        },
    )

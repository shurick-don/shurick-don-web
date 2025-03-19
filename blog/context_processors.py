from .models import Category
from django.db import models

def get_categories(request):
    """
    Метод, определяющий кол-во статей, которые были опубликованы в каждой из категорий
    """
    qs = Category.objects.all()  # Получение всех объектов модели категорий
    
    # Не сработало((
    # qs = qs.annotate(articles_count=Count('articles'), filter=Q(articles__status=Article.Status.PUBLISHED))

    #  Создание нового поля "articles_count" в qs, в который передается сумма статей со статусом = 1 (PUBLISHED)
    qs = qs.annotate(articles_count=models.Sum(
        models.Case(
            models.When(articles__status=True, then=1),
            default=0, output_field=models.IntegerField()
        )))

    return {'categories': qs}
from io import BytesIO
import os
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field

from utils import unique_slugify, image_compress


class Category(MPTTModel):
    """
    Модель категорий со вложенностью
    """

    # Поле заголовка. CharField для короткого и точного текстового описания (20 символов)
    title = models.CharField(max_length=20, verbose_name="Название категории")
    # Поле slug. SlugField для URL категории, уникальное
    slug = models.SlugField(max_length=20, verbose_name="URL категории", unique=True)
    # Поле описания категории
    description = models.TextField(verbose_name="Описание категории", max_length=100)
    parent = TreeForeignKey(
        "self",  # Внешний ключ ссылается на ту же модель, в которой он определен, то есть на Category
        on_delete=models.CASCADE,  # Если родительская категория удалена, то все дочерние категории также будут удалены
        null=True,  # Допустимо значение Null
        blank=True,  # Может быть пустым
        db_index=True,  # Индексация поля для ускорения поиска / сортировки по полю
        related_name="children",  # Имя обратной связи между родительской и дочерней категорией
        verbose_name="Родительская категория",  # Название родительской категории, отображаемое в админ-панели
    )

    class MPTTMeta:
        """
        Метамодель: сортировка по вложенности
        """

        order_insertion_by = ("title",)

    class Meta:
        """
        Метамодель: названия полей в админ-панели
        """

        db_table = "app_category"  # Название таблицы в БД
        verbose_name = "Категория"  # Имя в единственном числе (для админ-панели)
        verbose_name_plural = (
            "Категории"  # Имя во множественном числе (для админ-панели)
        )

    def __str__(self):
        """
        Переопределение метода __str__ для понятного представления объекта модели (возвращается название).
        - Вывод стандартного метода: <QuerySet [<Category:>,<Category:>,<Category:>....]
        - Вывод переопределенного метода: <QuerySet [<Category:ееTitle>,<Category:ееTitle>,<Category:ееTitle>....]
        """
        return self.title

    def get_absolute_url(self):
        """
        Метод, формирующий корректный URL адрес категории. Позволяет узнать канонический путь представления (в данном
        случае 'articles_by_category' - имя, заданное в urls.py -> urlpatterns)
        """
        return reverse("articles_by_category", kwargs={"slug": self.slug})


def article_media_path(instance, file):
    """
    Функция переопределяющая директорию сохранения файлов поста в media на
    'blog/"article id. Название поста"/"Название файла"'
    """
    return "blog/thumbnails/Thmb.id_to_replace. {0}".format(file)


class Article(models.Model):
    """
    Модель статей для сайта
    """

    class ArticleManager(models.Manager):
        """
        Кастомный менеджер для модели статей
        """

        def all(self):
            """
            Переопределения метода all, возвращающего список статей: только со статусом "published"
            """
            return (
                self.get_queryset()
                .select_related("category")
                .filter(status=Article.Status.PUBLISHED)
            )

        # Данный метод отрабатывает и в админ-панели (а это не нужно), поэтому им не пользуемся
        # def get_queryset(self):
        #     """
        #     Переопределения метода get_queryset, возвращающего список статей: только со статусом "published"
        #     """
        #     return super().get_queryset().select_related('category').filter(status=Article.Status.PUBLISHED)

    class Status(models.IntegerChoices):
        """
        Класс статусов для статьи:
        - bool (0 / 1) для отображения в БД
        - str для отображения в формах и админ-панели
        """

        DRAFT = (0, "Черновик")
        PUBLISHED = (1, "Опубликовано")

    # Поле заголовка. CharField для короткого и точного текстового описания (50 символов)
    title = models.CharField(verbose_name="Заголовок", max_length=50)
    # Поле slug. SlugField для URL статьи, уникальное
    slug = models.SlugField(verbose_name="URL", max_length=55, unique=True)
    # Поле короткого описания для отображения в превью статьи
    short_description = models.CharField(
        max_length=500, verbose_name="Краткое описание"
    )
    # Поле полного описания
    full_description = models.TextField(verbose_name="Полное описание")
    # Поле превью. ImageField для валидации и загрузки изображения
    thumbnail = models.ImageField(
        upload_to=article_media_path,  # Путь сохранения
        verbose_name="Превью поста",  # Имя (для админ-панели)
        validators=[
            FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg", "webp"))
        ],  # Валидация допустимых форматов
    )
    # Поле статуса (опубликовано / черновик). В БД хранится bool, но для лучшего восприятия отображаются Status.choices
    status = models.BooleanField(
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
        default=Status.PUBLISHED,
        verbose_name="Статус поста",
        max_length=10,
    )
    # Поле даты создания статьи. DateTimeField с автоматическим добавлением метки (не редактируемое, editable=False)
    time_create = models.DateTimeField(
        auto_now_add=True, verbose_name="Время добавления"
    )
    # Поле даты обновления статьи. DateTimeField с автоматическим добавлением метки (не редактируемое, editable=False)
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    # Поле категория. TreeForeignKey для внешнего ключа модели Category (т.к. она наследуется от MPTTModel)
    category = TreeForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="Категория",
    )
    # Поле полного описания через CKEditor5 (расширенный редактор текста)
    full_description = CKEditor5Field(verbose_name='Полное описание', config_name='extends')

    # Вызов и сохранение объектов модели через кастомный менеджер
    objects = ArticleManager()

    class Meta:
        """
        Метамодель: сортировка, названия полей в админ-панели
        """

        db_table = "app_article"  # Название таблицы в БД
        ordering = ["-time_create"]  # Сортировка от новых статей к старым
        verbose_name = "Статья"  # Имя в единственном числе (для админ-панели)
        verbose_name_plural = "Статьи"  # Имя во множественном числе (для админ-панели)

    def __str__(self):
        """
        Переопределение метода __str__ для понятного представления объекта модели (возвращается название).
        - Вывод стандартного метода: <QuerySet [<Article:>,<Article:>,<Article:>....]
        - Вывод переопределенного метода: <QuerySet [<Article:егоTitle>,<Article:егоTitle>,<Article:егоTitle>....]
        """
        return self.title

    def get_absolute_url(self):
        """
        Метод, формирующий корректный URL адрес статьи. Позволяет узнать канонический путь представления (в данном
        случае 'article' - имя, заданное в urls.py -> urlpatterns)
        """
        return reverse("article", kwargs={"slug": self.slug})


@receiver(pre_save, sender=Article)
def prepopulated_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = unique_slugify(instance, instance.title)


@receiver(pre_save, sender=Article)
def article_delete_thumbnail_on_update(sender, instance, **kwargs):
    """
    Функция удаления превью модели из папки 'media' при обновлении объекта модели, а также сжатия фото
    """
    # Попробовать получить файл со старым превью по ключу объекта
    try:
        thumbnail_old = sender.objects.get(pk=instance.pk).thumbnail
    except sender.DoesNotExist:  # Если объект еще не создан - передать сжатое фото
        instance.thumbnail = image_compress(instance.thumbnail, width=600)
        return False

    thumbnail_new = instance.thumbnail  # Новое превью = загруженное превью объекта

    # Если новое превью отличается от старого (в случае обновления поля отличного от изображения)
    if not thumbnail_old == thumbnail_new:
        if (
            "id_to_replace" not in thumbnail_old.path
        ):  # Если превью загружено впервые (старого нет)
            instance.thumbnail = image_compress(
                instance.thumbnail, width=600
            )  # Передать сжатое фото
        if os.path.isfile(
            thumbnail_old.path
        ):  # Если путь к файлу старого превью существует
            os.remove(thumbnail_old.path)  # Удалить путь к файлу старого превью


@receiver(post_save, sender=Article)
def update_thumbnail_name(sender, instance, **kwargs):
    """
    Функция переименования превью модели при первичном сохранении (для передачи в название id)
    """
    thumbnail_old = sender.objects.get(pk=instance.pk).thumbnail  # Поле старого превью

    # Если в названии превью присутствует "id_to_replace" (который задан по умолчанию в article_media_path)
    if "id_to_replace" in thumbnail_old.path:
        # Новый путь превью = старый путь, с замененным "id_to_replace" на id объекта
        thumbnail_new_path = thumbnail_old.path.replace(
            "id_to_replace", str(instance.pk)
        )
        # Новое имя превью = старое имя, с замененным "id_to_replace" на id объекта
        thumbnail_new_name = thumbnail_old.name.replace(
            "id_to_replace", str(instance.pk)
        )
        # Переименование пути до превью
        os.rename(thumbnail_old.path, thumbnail_new_path)
        # Переименование превью в объекте модели
        instance.thumbnail = thumbnail_new_name
        # Сохранение объекта модели
        instance.save()
    else:
        return False


@receiver(pre_delete, sender=Article)
def article_delete_thumbnail_on_delete(sender, instance, **kwargs):
    """
    Функция удаления превью модели из папки 'media' при удалении объекта модели
    """
    # Необходимо передать значение false, чтобы FileField не сохранил модель
    if instance.thumbnail:
        instance.thumbnail.delete(False)

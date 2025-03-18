import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files import File
from django.db import models
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from .utils import image_compress


class Gallery(models.Model):
    """
    Модель галереи для сайта
    """

    # Поле заголовка. CharField для короткого и точного текстового описания (25 символов)
    title = models.CharField(max_length=25, verbose_name="Заголовок")
    # Поле описания. CharField для короткого и точного текстового описания (50 символов)
    content = models.CharField(max_length=50, verbose_name="Описание")
    # Поле превью (сжатое фото). ImageField для валидации и загрузки изображения
    photo_compressed = models.ImageField(
        upload_to="gallery",  # Путь сохранения
        verbose_name="Фото (сжатое)",  # Имя (для админ-панели)
        validators=[
            FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg"))
        ],  # Валидация допустимых форматов
        blank=True,  # Может быть пустым
    )
    # Поле фото (в полном разрешении). ImageField для валидации и загрузки изображения
    photo_full = models.ImageField(
        upload_to="gallery",  # Путь сохранения
        verbose_name="Фото (HD)",  # Имя (для админ-панели)
        validators=[
            FileExtensionValidator(allowed_extensions=("png", "jpg", "jpeg"))
        ],  # Валидация допустимых форматов
    )

    class Meta:
        """
        Метамодель: сортировка, названия полей в админ-панели
        """

        ordering = ["-pk"]  # Сортировка по id (от новых к старым)
        verbose_name = "Фотографии"  # Имя в единственном числе (для админ-панели)
        verbose_name_plural = (
            "Фотографии"  # Имя во множественном числе (для админ-панели)
        )

    def __str__(self):
        """
        Переопределение метода __str__ для понятного представления объекта модели (возвращается название).
        - Вывод стандартного метода: <QuerySet [<Gallery:>,<Gallery:>,<Gallery:>....]
        - Вывод переопределенного метода: <QuerySet [<Gallery:ееTitle>,<Gallery:ееTitle>,<Gallery:ееTitle>....]
        """
        return self.title


@receiver(pre_save, sender=Gallery)
def gallery_photo_update(sender, instance, **kwargs):
    """
    Функция добавления в объект модели фото и сжатого фото, а также удаления старых, если они есть
    """

    try:  # Попробовать получить файлы со старыми фото по ключу объекта
        photo_old = sender.objects.get(pk=instance.pk).photo_full
        photo_compressed_old = sender.objects.get(pk=instance.pk).photo_compressed
    except sender.DoesNotExist:  # Если объект еще не создан - передать сжатое фото
        instance.photo_compressed = image_compress(instance.photo_full, width=700)
        return False

    photo_new = instance.photo_full  # Новое фото = загруженное фото (full)
    if not photo_old == photo_new:  # Если новое фото отличается от старого
        instance.photo_compressed = image_compress(instance.photo_full, width=700)
        if photo_old and os.path.isfile(
            photo_old.path
        ):  # Если путь к файлу старого фото (full) существует
            os.remove(photo_old.path)  # Удалить путь к файлу старого фото (full)
        if photo_compressed_old and os.path.isfile(
            photo_compressed_old.path
        ):  # Если путь к файлу старого фото (full) существует
            os.remove(
                photo_compressed_old.path
            )  # Удалить путь к файлу старого фото (full)


@receiver(pre_delete, sender=Gallery)
def gallery_delete(sender, instance, **kwargs):
    """
    Функция удаления превью модели из папки 'media' при удалении объекта модели
    """
    # В качестве аргумента delete необходимо передать значение false, чтобы FileField не сохранил модель
    if instance.photo_compressed:  # Если фото (compressed) существует
        instance.photo_compressed.delete(False)  # Удалить
    if instance.photo_full:  # Если фото (full) существует
        instance.photo_full.delete(False)  # Удалить

from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files import File


def image_compress(image, width):
    """
    Метод для сжатия загруженного фото и конвертации в webp
    """
    im = Image.open(
        image
    )  # Передаем переменной im открыть и идентифицировать файл изображения
    aspect_ratio = im.size[0] / im.size[1]  # Расчет соотношения сторон
    height = int(width / aspect_ratio)  # Расчет высоты сжатого изображения
    im = im.resize(
        (width, height)
    )  # Меняем разрешение изображения на рассчитанное выше
    im_bytes = BytesIO()  #  Создание потока, использующего буфер байтов в памяти
    im.save(
        fp=im_bytes, format="WEBP", quality=100
    )  # Выбираем формат выходного изображения и его качество
    image_content_file = ContentFile(
        content=im_bytes.getvalue()
    )  # Получаем байтовое значение файла
    name = f'{".".join(image.name.split(".")[0:-1])}_compressed.WEBP'  # Переименовываем файл
    image_compressed = File(image_content_file, name=name)  # Сохраняем файл
    return image_compressed


navigation = [
    {"title": "Фото", "url_name": "gallery"},  # request.path = 'gallery/'
]


article_actions = []


class DataMixin:
    """
    Класс миксиана с навигацией и опциями редактирования статьи
    """

    def get_mixin_context(self, **kwargs):
        """
        Метод получения контекста
        """
        context = kwargs  # Получаем исходный контекст

        context["nav"] = navigation  # Расширяем словарь контекста новым ключом 'nav'
        context[
            "article_actions"
        ] = article_actions  # Расширяем словарь контекста новым ключом 'article_actions'

        return context

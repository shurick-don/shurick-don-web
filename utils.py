from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files import File
from uuid import uuid4


navigation = [{'title': 'Обо мне', 'url_name': 'main'},  # request.path = ''
              {'title': 'Фото', 'url_name': 'gallery'},  # request.path = 'gallery/'
              {'title': 'Блог', 'url_name': 'blog'},  # request.path = 'blog/'
              {'title': 'Добавить пост', 'url_name': 'article_create'}  # request.path = 'blog/articles/create/'
              ]

article_actions = [{'title': 'Редактировать статью', 'url_name': 'article_update'}]

class DataMixin:
    """
    Класс миксиана с навигацией и опциями редактирования статьи
    """
    def get_mixin_context(self, **kwargs):
        """
        Метод получения контекста
        """
        context = kwargs  # Получаем исходный контекст
        user_nav = navigation.copy()  # Копируем навигацию, чтоб внесенные далее изменения не затрагивали исходную

        if not self.request.user.is_authenticated:  # Если пользователь не авторизован
            user_nav.pop(-1)  # Убрать из меню навигации путь для добавления статьи

        context['nav'] = user_nav  # Расширяем словарь контекста новым ключом 'nav'
        context['article_actions'] = article_actions  # Расширяем словарь контекста новым ключом 'article_actions'

        return context




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






from pytils.translit import slugify

def unique_slugify(instance, slug):
    """
    Функция: генерация уникального SLUG для объекта модели
    """
    model = instance.__class__  # Получаем модель по объекту
    unique_slug = slugify(slug)  # Формируем уникальный slug из переданного функции аргумента slug
    while model.objects.filter(slug=unique_slug).exists():  # Пока наш уникальный slug повторяет другой
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'  # Сформируем новый slug
    return unique_slug


    class CkeditorCustomStorage(FileSystemStorage):
        """
        Кастомное расположение для медиа файлов редактора
        """
        def _save(self, name, content):
            folder_name = datetime.now().strftime('%Y/%m/%d')  # Присваиваем имя папки в формате (год > месяц > день)
            name = os.path.join(folder_name, name)  # Включаем в имя файла расположение в соответсвующих дате папках
            return super()._save(name, content)

        location = os.path.join(settings.MEDIA_ROOT, 'blog/uploads/')  # Абсолютный путь к каталогу, в котором будут храниться файлы
        base_url = urljoin(settings.MEDIA_URL, 'blog/uploads/')  # URL-адрес, по которому хранятся файлы в этом каталоге
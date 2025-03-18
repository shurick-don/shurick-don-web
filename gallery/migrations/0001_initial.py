# Generated by Django 5.1.7 on 2025-03-18 01:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Gallery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=25, verbose_name="Заголовок")),
                ("content", models.CharField(max_length=50, verbose_name="Описание")),
                (
                    "photo_compressed",
                    models.ImageField(
                        blank=True,
                        upload_to="gallery",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=("png", "jpg", "jpeg")
                            )
                        ],
                        verbose_name="Фото (сжатое)",
                    ),
                ),
                (
                    "photo_full",
                    models.ImageField(
                        upload_to="gallery",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=("png", "jpg", "jpeg")
                            )
                        ],
                        verbose_name="Фото (HD)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Фотографии",
                "verbose_name_plural": "Фотографии",
                "ordering": ["-pk"],
            },
        ),
    ]

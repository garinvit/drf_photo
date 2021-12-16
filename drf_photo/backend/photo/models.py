from django.db import models

# Create your models here.
from garpixcms import settings


class AlbumTags(models.Model):
    title = models.CharField(max_length=100, verbose_name='Тэг альбома')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тэг альбомов"
        verbose_name_plural = "Тэги для альбомов"


class PhotoTags(models.Model):
    title = models.CharField(max_length=100, verbose_name='Тэг фото')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тэг для фотографий"
        verbose_name_plural = "Тэги для фотографий"



class Album(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название альбома')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    description = models.CharField(max_length=255, verbose_name='Описание альбома', blank=True)
    tags = models.ManyToManyField(AlbumTags, blank=True, verbose_name='Тэги для альбома')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"


class Photo(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название фото')
    description = models.CharField(max_length=255, verbose_name='Описание фото', blank=True)
    tags = models.ManyToManyField(PhotoTags, blank=True, verbose_name='Тэги для альбома')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    image = models.ImageField(verbose_name='Фото', blank=True)
    image_small = models.ImageField(verbose_name='Фото', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фотографии"

import sys

from django.db import models
from garpixcms import settings
from django.core.exceptions import ValidationError



def file_size(value): # add this to some file where you can import it from
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 2 MiB.')

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}/{2}'.format(instance.author.id, instance.album.id, filename)


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
    def validate_image(self):
        # print(self, dir(self))
        # print(self.file.content_type)
        try:
            content_type = self.content_type
        except AttributeError:
            content_type = self.file.content_type
        filesize = self.size
        content_allow = ('image/jpeg', 'image/jpg', 'image/png')
        megabyte_limit = 5.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
        if content_type not in content_allow:
            raise ValidationError('Не верный формат. Возможны только png, jpg, jpeg.')

    title = models.CharField(max_length=100, verbose_name='Название фото')
    description = models.CharField(max_length=255, verbose_name='Описание фото', blank=True)
    tags = models.ManyToManyField(PhotoTags, blank=True, verbose_name='Тэги для альбома')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    image = models.ImageField(verbose_name='Фото', blank=True, upload_to=user_directory_path, validators=[validate_image])
    image_small = models.ImageField(verbose_name='Фото', blank=True, upload_to=user_directory_path)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фотографии"

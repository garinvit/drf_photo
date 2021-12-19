from django.db import models
from garpixcms import settings
from PIL import Image
from django.core.exceptions import ValidationError


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}/{2}'.format(instance.author.id, instance.album.id, filename)


def user_directory_path_small(instance, filename):
    return 'user_{0}/{1}/small_{2}'.format(instance.author.id, instance.album.id, filename)


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
        null=True,
    )
    description = models.CharField(max_length=255, verbose_name='Описание альбома', blank=True)
    tags = models.ManyToManyField(AlbumTags, blank=True, verbose_name='Тэги для альбома')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def get_photo_count(self):
        # return len(self.photo_set.all())
        return self.photo_set.count()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"
        ordering = ("-created_at",)


class Photo(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название фото')
    description = models.CharField(max_length=255, verbose_name='Описание фото', blank=True)
    tags = models.ManyToManyField(PhotoTags, blank=True, verbose_name='Тэги для альбома')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    image = models.ImageField(verbose_name='Фото', blank=True, upload_to=user_directory_path) # , validators=[validate_image]
    image_small = models.ImageField(verbose_name='Уменьшенное фото', blank=True, upload_to=user_directory_path_small)
    album = models.ForeignKey(Album, null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.image.name:
            if 'content_type' in dir(self.image.file):  #иначе файл был уже добавлен
                img_file = self.image.file
                content_allow = ('image/jpeg', 'image/jpg', 'image/png')
                megabyte_limit = 5.0
                content_type = img_file.content_type
                if img_file.size > megabyte_limit*1024*1024:
                    raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
                if content_type not in content_allow:
                    raise ValidationError('Не верный формат. Возможны только png, jpg, jpeg.')
        else:
            self.image_small.delete()
        # raise ValidationError('Test')

        super().save(*args, **kwargs)
        if self.image_small.name:
            img = Image.open(self.image_small.path)
            width, height = img.size
            fixed = 150
            if width >= height:
                percent = (float(height) / float(width))
                other_size = int((float(fixed) * float(percent)))
                img = img.resize((fixed, other_size))
            else:
                percent = (float(width) / float(height))
                other_size = int((float(fixed) * float(percent)))
                img = img.resize((other_size, fixed))
            img.save(self.image_small.path)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фотографии"
        ordering = ("-created_at",)


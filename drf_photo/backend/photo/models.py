import os
from django.db import models
# from django.db.models.signals import post_delete
# from django.dispatch import receiver
from garpixcms import settings
from PIL import Image
from django.core.exceptions import ValidationError


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}/{2}'.format(instance.get_author(), instance.album.id, os.path.basename(filename))


def user_directory_path_small(instance, filename):
    return 'user_{0}/{1}/small_{2}'.format(instance.get_author(), instance.album.id, os.path.basename(filename))


def validate_image(file):
    content_type = ""
    megabyte_limit = 5.0
    content_allow = ('image/jpeg', 'image/jpg', 'image/png', '.jpeg', '.jpg', '.png')
    if file.size > megabyte_limit * 1024 * 1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))
    if 'content_type' in dir(file):
        content_type = file.content_type
    else:
        content_type = os.path.splitext(file.name)[1]
    if content_type.lower() not in content_allow:
        raise ValidationError('Не верный формат. Возможны только png, jpg, jpeg.')


class Tags(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название тэга')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"


class Album(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название альбома')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    description = models.CharField(max_length=255, verbose_name='Описание альбома', blank=True)
    tags = models.ManyToManyField(Tags, blank=True, verbose_name='Тэги для альбома')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def get_author(self):
        return self.author.id

    def get_photo_count(self):
        return self.photo_set.count()

    def get_photo_from_album(self):
        return self.photo_set.all()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"
        ordering = ("-created_at",)


class Photo(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название фото')
    description = models.CharField(max_length=255, verbose_name='Описание фото', blank=True)
    tags = models.ManyToManyField(Tags, blank=True, verbose_name='Тэги для альбома')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    image = models.ImageField(verbose_name='Фото', blank=True,
                              upload_to=user_directory_path, validators=[validate_image])  #
    image_small = models.ImageField(verbose_name='Уменьшенное фото', blank=True, upload_to=user_directory_path_small)
    album = models.ForeignKey(Album, null=True, on_delete=models.CASCADE)

    def get_author(self):
        return self.album.author.id

    def save(self, *args, **kwargs):
        if self.image.name:  # проверка есть ли вообще файл, если нет то удалить и уменьшенный вариант
            if self.image.file.__class__.__name__ == "ImageFile":
                validate_image(self.image.file)
        if not self.image.name:
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

# @receiver(post_delete, sender=Photo)
# def post_save_image(sender, instance, *args, **kwargs):
#     """ Clean Old Image file """
#     print(instance, instance.image.file)
#     try:
#         instance.image.delete(save=False)
#     except Exception as e:
#         print(f"Delete file exception {e}")
#     try:
#         instance.image_small.delete(save=False)
#     except Exception as e:
#         print(f"Delete file exception {e}")

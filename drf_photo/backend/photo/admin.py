from django.contrib import admin
from .models import AlbumTags, Album, PhotoTags, Photo
# Register your models here.


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    pass


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass


admin.site.register(AlbumTags)
admin.site.register(PhotoTags)

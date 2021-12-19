from django.contrib import admin
from .models import AlbumTags, Album, PhotoTags, Photo
# Register your models here.


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "created_at"]
    readonly_fields = ('created_at',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "album", "created_at"]
    fields = ("title", "description", "author", "album", "image", "image_small", "created_at")
    readonly_fields = ('created_at', "image_small",)

    def save_model(self, request, obj, form, change):
        obj.image_small = request.FILES['image']
        super().save_model(request, obj, form, change)


admin.site.register(AlbumTags)
admin.site.register(PhotoTags)

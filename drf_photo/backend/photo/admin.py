from django.contrib import admin
from .models import Tags, Album, Photo
# Register your models here.


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "author", "created_at"]
    readonly_fields = ('created_at',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "album", "created_at"]
    fields = ("title", "description", "album", "tags", "image", "image_small", "created_at")
    readonly_fields = ('created_at', "image_small",)

    def save_model(self, request, obj, form, change):
        if request.FILES:
            obj.image_small = request.FILES.get('image')
        super().save_model(request, obj, form, change)


admin.site.register(Tags)

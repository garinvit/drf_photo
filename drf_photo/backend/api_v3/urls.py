from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AlbumViewSet, PhotoViewSet, TagsViewSet, CreateUserView

app_name = "api_v3"

router = DefaultRouter()
router.register(r'album', AlbumViewSet, basename='album')
router.register(r'photo', PhotoViewSet, basename='photo')
router.register(r'tags', TagsViewSet, basename='tags')
urlpatterns = router.urls

urlpatterns += [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('auth/', include(('garpix_auth.urls', 'garpix_auth'), namespace='garpix_auth')),
]

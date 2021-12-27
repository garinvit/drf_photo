from django.urls import path, include
from .views import CurrentUserView, CreateUserView, AlbumModelView, TagsView, PhotoModelView


app_name = "api_v2"

urlpatterns = [
    path('current-user/', CurrentUserView.as_view(), name='current-user'),
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('tags/', TagsView.as_view(), name='tags'),
    path('album/', AlbumModelView.as_view(), name='album'),
    path('photo/', PhotoModelView.as_view(), name='photo'),
    path('album/<int:pk>/', AlbumModelView.as_view(), name='album-pk'),
    path('photo/<int:pk>/', PhotoModelView.as_view(), name='photo-pk'),
    path('auth/', include(('garpix_auth.urls', 'garpix_auth'), namespace='garpix_auth')),
]

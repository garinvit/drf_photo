from django.urls import path, include
from .views import CurrentUserView, CreateUserView, AlbumModelView, PhotoTagslView, AlbumTagsView
from django.urls import path
from garpix_auth.rest.obtain_auth_token import obtain_auth_token


app_name = "api"

urlpatterns = [
    path('current-user/', CurrentUserView.as_view(), name='current-user'),
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('album-tags/', AlbumTagsView.as_view(), name='album-tags'),
    path('photo-tags/', PhotoTagslView.as_view(), name='photo-tags'),
    path('album/', AlbumModelView.as_view(), name='album'),
    # path('token-auth/', obtain_auth_token),
    path('auth/', include(('garpix_auth.urls', 'garpix_auth'), namespace='garpix_auth')),
]

from django.urls import path, include, re_path
from .views import CurrentUserView, CreateUserView, AlbumModelView, PhotoTagslView, AlbumTagsView, PhotoModelView
from garpix_auth.rest.obtain_auth_token import obtain_auth_token


app_name = "api"

urlpatterns = [
    path('current-user/', CurrentUserView.as_view(), name='current-user'),
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('album-tags/', AlbumTagsView.as_view(), name='album-tags'),
    path('photo-tags/', PhotoTagslView.as_view(), name='photo-tags'),
    path('album/', AlbumModelView.as_view(), name='album'),
    # re_path('album/(?P<ordering>.+)', AlbumModelView.as_view(), name='album-order'),
    path('photo/', PhotoModelView.as_view(), name='photo'),
    path('album/<int:pk>/', AlbumModelView.as_view(), name='album-pk'),
    path('photo/<int:pk>/', PhotoModelView.as_view(), name='photo-pk'),
    # path('token-auth/', obtain_auth_token),
    path('auth/', include(('garpix_auth.urls', 'garpix_auth'), namespace='garpix_auth')),
]

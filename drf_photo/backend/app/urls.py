from garpixcms.urls import *  # noqa
from django.urls import path, re_path, include
from garpix_auth.views import LogoutView, LoginView

urlpatterns = [
        path('api/v1/', include('api.urls')),
] + urlpatterns  # noqa



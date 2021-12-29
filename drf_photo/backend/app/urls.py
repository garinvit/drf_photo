from garpixcms.urls import *  # noqa
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    # path('api/v1/', include('api.urls', namespace='api_v1')),
    # path('api/v2/', include('api_v2.urls', namespace='api_v2')),
    path('api/v3/', include('api_v3.urls', namespace='api_v3')),
    # Optional UI:
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + urlpatterns  # noqa

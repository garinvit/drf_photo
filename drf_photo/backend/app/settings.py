from garpixcms.settings import *  # noqa

INSTALLED_APPS += [
    # "api",
    # "api_v2",
    "api_v3",
    "photo",
    'rest_framework_social_oauth2',
    'garpix_auth',
    'django_filters',
]

API_URL = "api/v3"

REST_FRAMEWORK.update({
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
})
log = 0
if log:
    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        }
    }

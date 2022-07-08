import os

from .base import DJANGO_ROOT

try:
    import envkey  # NOQA
except Exception:
    pass


DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'openownership.org',
    'staging.openownership.org',
    'www.openownership.org',
    'prod.openownership.org',
    'openownership.hactar.work'
]

ASSETS_DEBUG = False

ASSETS_AUTO_BUILD = False

DEFAULT_FILE_STORAGE = 'utils.storages.MediaRootS3BotoStorage'

COLLECTFAST_ENABLED = False

GZIP_CONTENT_TYPES = [
    'text/css',
    'application/javascript',
    'application/x-javascript',
    'text/javascript',
    'application/vnd.ms-fontobject',
    'application/font-sfnt',
    'application/font-woff',
    'image/x-icon'
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
}

WHITENOISE_MAX_AGE = 31557600

AWS_S3_CUSTOM_DOMAIN = ''
AWS_STORAGE_BUCKET_NAME = "openownership.org"

####################################################################################################
# Bugsnag
####################################################################################################

BUGSNAG = {
    "api_key": os.environ.get('BUGSNAG_API_KEY'),
    "project_root": DJANGO_ROOT,
    "release_stage": os.environ.get('SERVER_ENV', 'development'),
    "ignore_classes": [
        'django.http.Http404', 'django.http.response.Http404',
        'django.core.exceptions.PermissionDenied'
    ],
    "notify_release_stages": ["production", "staging"]
}


####################################################################################################
# Django-Cron
####################################################################################################


CRON_CLASSES = [
    "modules.notion.cron.SyncCountries",
    "modules.notion.cron.SyncCommitments",
    "modules.notion.cron.SyncRegimes",
]

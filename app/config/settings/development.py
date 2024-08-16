import os  # NOQA
from .base import *  # NOQA
from .base import STORAGES


DEBUG = True

BASE_URL = 'http://0.0.0.0:5000'
WAGTAILADMIN_BASE_URL = 'http://0.0.0.0:5000'
DOMAIN_NAME = 'openownership.org.test'
SITE_PORT = 5000

ALLOWED_HOSTS = ['*']


STATIC_URL = '/static/'
STATIC_ROOT = 'static'


PRIVATE_FOLDER = '/usr/srv/private/'
WAGTAIL_CACHE = True
TESTING = True


# CSRF cookies etc.
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
CSRF_HEADER_NAME = "X-CSRFToken"

####################################################################################################
# Serve media files from the staging CDN
####################################################################################################

"""
DEFAULT_FILE_STORAGE is now defined in base.py / STORAGES
"""

STORAGES['staticfiles']['BACKEND'] = 'django.contrib.staticfiles.storage.StaticFilesStorage'

AWS_S3_CUSTOM_DOMAIN = 'oo.cdn.ngo'
AWS_STORAGE_BUCKET_NAME = "openownership"

MEDIA_ROOT = 'staging/media/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_ROOT}'
#WAGTAIL_CACHE = False
#CACHEOPS_ENABLED = False

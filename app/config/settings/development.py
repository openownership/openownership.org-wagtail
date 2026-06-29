import os  # NOQA
from .base import *  # NOQA
from .base import STORAGES


DEBUG = True

BASE_URL: str = "https://openownership.test"
WAGTAILADMIN_BASE_URL: str = BASE_URL
DOMAIN_NAME = "openownership.test"
SITE_PORT = 5000

ALLOWED_HOSTS = ["*"]


STATIC_URL = "/static/"
STATIC_ROOT = "static"


PRIVATE_FOLDER = "/usr/srv/private/"
WAGTAIL_CACHE = True
TESTING = True


# CSRF cookies etc.
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
CSRF_HEADER_NAME = "X-CSRFToken"
CSRF_TRUSTED_ORIGINS = [
    "http://openownership.test",
    "https://openownership.test",
]

####################################################################################################
# Serve media files from the staging CDN
####################################################################################################

"""
DEFAULT_FILE_STORAGE is now defined in base.py / STORAGES
"""

STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.StaticFilesStorage"

AWS_S3_CUSTOM_DOMAIN = "oo.hacdn.io"
AWS_STORAGE_BUCKET_NAME = "openownership"

MEDIA_ROOT = "staging/media/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_ROOT}"
# WAGTAIL_CACHE = False
# CACHEOPS_ENABLED = False

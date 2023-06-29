from __future__ import absolute_import, unicode_literals
import os  # NOQA
from .base import *  # NOQA


DEBUG = True

BASE_URL = 'http://0.0.0.0:5000'
WAGTAILADMIN_BASE_URL = 'http://0.0.0.0:5000'

COLLECTFAST_ENABLED = False

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

ALLOWED_HOSTS = ['*']

ASSETS_DEBUG = True

ASSETS_AUTO_BUILD = True

STATIC_ROOT = 'static'
MEDIA_ROOT = '/usr/srv/app/media'

PRIVATE_FOLDER = '/usr/srv/private/'

DOMAIN_NAME = 'openownership.org.test'
SITE_PORT = 5000

WAGTAIL_CACHE = True

TESTING = True


# CSRF cookies etc.
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
CSRF_HEADER_NAME = "X-CSRFToken"

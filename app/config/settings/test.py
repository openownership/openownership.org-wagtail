import os

from .base import *  # NOQA
from .base import STORAGES, CACHES

DEBUG = True

BASE_URL = 'http://openownership.org.test:5000'
WAGTAILADMIN_BASE_URL = 'http://openownership.org.test:5000'

COLLECTFAST_ENABLED = False

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

SECRET_KEY = 'DOESNTMATTERINTESTS'  # noqa: S105

ALLOWED_HOSTS = ['*']

ASSETS_DEBUG = True
ASSETS_AUTO_BUILD = True

WAGTAIL_CACHE = False

TESTING = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

# Change the numbers of the databases to avoid conflicting cache data
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
CACHES['default']['LOCATION'] = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/2'
CACHES['wagtailcache']['LOCATION'] = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/3'


STORAGES["staticfiles"]["BACKEND"] = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    },
}

import os
env = os.environ.get('SERVER_ENV')
sf = "[%(asctime)s] %(levelname)s [NLT - {}] [%(name)s:%(lineno)s] %(message)s".format(env)

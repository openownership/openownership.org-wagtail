from __future__ import absolute_import, unicode_literals

from .base import *  # NOQA

DEBUG = True

BASE_URL = 'http://openownership.org.test:5000'
WAGTAILADMIN_BASE_URL = 'http://openownership.org.test:5000'

COLLECTFAST_ENABLED = False

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

SECRET_KEY = 'DOESNTMATTERINTESTS'

ALLOWED_HOSTS = ['*']

ASSETS_DEBUG = True
ASSETS_AUTO_BUILD = True

WAGTAIL_CACHE = False

TESTING = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.StaticFilesStorage'
)

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    },
}

import os
env = os.environ.get('SERVER_ENV')
sf = "[%(asctime)s] %(levelname)s [NLT - {}] [%(name)s:%(lineno)s] %(message)s".format(env)

from __future__ import absolute_import, unicode_literals

from .base import *  # NOQA

DEBUG = True

BASE_URL = 'http://openownership.org.test:5000'

COLLECTFAST_ENABLED = False

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'DOESNTMATTERINTESTS'

ALLOWED_HOSTS = ['*']

ASSETS_DEBUG = True
ASSETS_AUTO_BUILD = True

WAGTAIL_CACHE = False

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
        'BACKEND': 'wagtail.search.backends.db',
    },
}

import os
env = os.environ.get('SERVER_ENV')
sf = "[%(asctime)s] %(levelname)s [NLT - {}] [%(name)s:%(lineno)s] %(message)s".format(env)

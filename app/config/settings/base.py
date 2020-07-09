# -*- coding: utf-8 -*-

"""
Django settings for the TEMPLATEPROJECT_FULL_NAME project.
"""

from __future__ import absolute_import, unicode_literals

# stdlib
import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import datetime, timedelta

# 3rd party
import envkey  # NOQA
from loguru import logger as guru


SHELL_PLUS = "ipython"
PROJECT_DIR_NAME = 'app'

DJANGO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES_DIR = os.path.join(DJANGO_ROOT, PROJECT_DIR_NAME)


the_future = datetime.now() + timedelta(days=365 * 1)
guru.add("/var/log/TEMPLATEPROJECT_SHORT_NAME/output.log", rotation="100 MB", backtrace=True)


####################################################################################################
# Installed Apps
####################################################################################################

DJANGO_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    "django.contrib.sitemaps",
    'rest_framework',
    'django_extensions',
    'modelcluster',
    'taggit',
    'storages',
    'django.contrib.staticfiles',
    'cacheops',
]

WAGTAIL_APPS = [
    'wagtailcache',
    'wagtail.api.v2',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.contrib.postgres_search',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.contrib.forms',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.settings',
    'wagtail.contrib.table_block',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.search_promotions',
    'wagtailfontawesome',
]

SITE_APPS = [
    'modules.users',
    'modules.core',
]

INSTALLED_APPS = DJANGO_APPS + WAGTAIL_APPS + SITE_APPS


####################################################################################################
# Middleware
####################################################################################################

MIDDLEWARE = [
    'wagtailcache.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'bugsnag.django.middleware.BugsnagMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'wagtailcache.cache.FetchFromCacheMiddleware',
]


####################################################################################################
# Core Django config
####################################################################################################

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
BASE_URL = 'https://TEMPLATEPROJECT_DOMAIN'
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
INTERNAL_IPS = ['127.0.0.1']
APPEND_SLASH = True
AUTH_USER_MODEL = 'users.User'


####################################################################################################
# Database
####################################################################################################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', 5432),
    }
}

REDIS_CONNECTION = 'redis://{}:6379/0'.format(os.environ.get('REDIS_HOST'))


####################################################################################################
# Cache
####################################################################################################

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
WAGTAIL_CACHE = True
WAGTAIL_CACHE_BACKEND = 'wagtailcache'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:6379/0',
        'OPTIONS': {
            "PARSER_CLASS": "redis.connection.HiredisParser",
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': os.environ.get('REDIS_PASSWORD'),
            "IGNORE_EXCEPTIONS": True
        }
    },
    'wagtailcache': {
        "BACKEND": "wagtailcache.compat_backends.django_redis.RedisCache",
        'LOCATION': f'redis://{REDIS_HOST}:6379/1',
        'TIMEOUT': 60 * 60 * 24 * 7,
        'OPTIONS': {
            "PARSER_CLASS": "redis.connection.HiredisParser",
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': os.environ.get('REDIS_PASSWORD'),
            "IGNORE_EXCEPTIONS": True
        }
    },
}

CACHEOPS_REDIS = {
    'host': os.environ.get('REDIS_HOST'),
    'port': 6379,
    'db': 2,
    'socket_timeout': 3,
    'password': os.environ.get('REDIS_PASSWORD', None)
}


CACHEOPS = {
    'users.User': {'ops': 'all', 'timeout': 60 * 60},
    'auth.Group': {'ops': 'all', 'timeout': 60 * 60},
    'wagtailimages.Image': {'ops': 'all', 'timeout': 60 * 60},
    'wagtailimages.Rendition': {'ops': 'all', 'timeout': 60 * 60},
    'migrations.*': {'ops': (), 'timeout': 0},
    'core.MetaTagSettings': {'ops': 'all', 'timeout': 60 * 60 * 24 * 7},
    'core.SocialMediaSettings': {'ops': 'all', 'timeout': 60 * 60 * 24 * 7},
    'core.NavItem': {'ops': 'all', 'timeout': 60 * 60 * 24 * 7},
    'core.NavigationMenu': {'ops': 'all', 'timeout': 60 * 60 * 24 * 7},
    '*.*': {'ops': (), 'timeout': 60 * 60},
}

CACHEOPS_ENABLED = True
CACHEOPS_DEGRADE_ON_FAILURE = True


####################################################################################################
# Search
####################################################################################################


WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.contrib.postgres_search.backend',
        'SEARCH_CONFIG': 'english',
        'AUTO_UPDATE': True
    },
}


####################################################################################################
# Template
####################################################################################################

JINJA2_EXTENSIONS = [
    'wagtail.core.jinja2tags.core',
    'wagtail.admin.jinja2tags.userbar',
    'wagtail.images.jinja2tags.images',
    'jinja2.ext.with_',
    'jinja2.ext.i18n',
    'wagtail.contrib.settings.jinja2tags.settings',
    'config.template.TemplateGlobalsExtension',
    "jinja2.ext.do",
    "jinja2.ext.loopcontrols",
    "jinja2.ext.autoescape",
    'cacheops.jinja2.cache'
]

DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.jinja'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            os.path.join(DJANGO_ROOT, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS':{
            'extensions': JINJA2_EXTENSIONS,
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(DJANGO_ROOT, 'templates', 'django')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "django.template.context_processors.static"
            ],
        },
    },
]


####################################################################################################
# Assets
####################################################################################################

STATIC_ROOT = os.path.join(DJANGO_ROOT, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(DJANGO_ROOT, 'media')
MEDIA_URL = '/media/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(DJANGO_ROOT, 'assets', 'dist'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

####################################################################################################
# AWS
####################################################################################################

AWS_HEADERS = {
    'Expires': the_future.strftime('%a, %d %b %Y %H:%M:%S'),
    'Cache-Control': 'max-age=2628000',
}

AWS_S3_OBJECT_PARAMETERS = {
    'Expires': the_future.strftime('%a, %d %b %Y %H:%M:%S'),
    'CacheControl': 'max-age=2628000',
}

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_BUCKET')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')


AWS_S3_FILE_OVERWRITE = False
AWS_IS_GZIPPED = True
AWS_S3_SECURE_URLS = True
AWS_PRELOAD_METADATA = False
AWS_DEFAULT_ACL = 'public-read'

####################################################################################################
# Email
####################################################################################################

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST_URL', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
EMAIL_USE_TLS = True
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = ''

WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = 'wagtail@TEMPLATEPROJECT_DOMAIN'


####################################################################################################
# ReCaptcha§
####################################################################################################

RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')


####################################################################################################
# Project specific settings
####################################################################################################

WAGTAILMENUS_USE_BACKEND_SPECIFIC_TEMPLATES = True
# AUTH_USER_MODEL = 'users.User'
WAGTAILDOCS_DOCUMENT_MODEL = 'core.SiteDocument'
WAGTAILIMAGES_IMAGE_MODEL = 'core.SiteImage'
IMAGE_MODEL = WAGTAILIMAGES_IMAGE_MODEL
DOCUMENT_MODEL = 'core.SiteDocument'


SITE_NAME = 'TEMPLATEPROJECT_FULL_NAME'
WAGTAIL_SITE_NAME = SITE_NAME

slideshare = {
    "endpoint": "https://www.slideshare.net/api/oembed/2",
    'urls': [
        "^http[s]?://www\\.slideshare\\.net/.+$"
    ]
}

soundcloud = {
    "endpoint": "https://soundcloud.com/oembed",
    "urls": [
        "^https://(?:m\\.)?soundcloud\\.com/[^#?/]+/.+$",
    ],
}

WAGTAILEMBEDS_FINDERS = [
    {
        'class': 'wagtail.embeds.finders.oembed',
        'providers': [slideshare, soundcloud]
    },
    {
        'class': 'wagtail.embeds.finders.oembed',
    },
]

DEFAULT_OBJECTS_PER_PAGE = 20

CSRF_COOKIE_HTTPONLY = True

ERROR_400_TEMPLATE_NAME = 'errors/500.html'
ERROR_404_TEMPLATE_NAME = 'errors/404.html'
ERROR_500_TEMPLATE_NAME = 'errors/500.html'

PRIVATE_FOLDER = '/srv/private/'

THEME_CHOICES = [

]

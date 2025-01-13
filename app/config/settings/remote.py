DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'openownership.org',
    'staging.openownership.org',
    'www.openownership.org',
    'prod.openownership.org',
    'openownership.hactar.work',
]


GZIP_CONTENT_TYPES = [
    'text/css',
    'application/javascript',
    'application/x-javascript',
    'text/javascript',
    'application/vnd.ms-fontobject',
    'application/font-sfnt',
    'application/font-woff',
    'image/x-icon',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

WHITENOISE_MAX_AGE = 31557600


####################################################################################################
# Django-Cron
####################################################################################################


CRON_CLASSES = [
    "modules.notion.cron.SyncCountries",
    "modules.notion.cron.SyncCommitments",
    "modules.notion.cron.SyncRegimes",
]


# CSRF cookies etc.
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False

DEBUG = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "openownership.org",
    "staging.openownership.org",
    "www.openownership.org",
    "prod.openownership.org",
    "openownership.hactar.work",
]


GZIP_CONTENT_TYPES = [
    "text/css",
    "application/javascript",
    "application/x-javascript",
    "text/javascript",
    "application/vnd.ms-fontobject",
    "application/font-sfnt",
    "application/font-woff",
    "image/x-icon",
]

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

WHITENOISE_MAX_AGE = 31557600


# Caddy terminates TLS and proxies to Django over plain http, so without this
# Django sees every request as insecure: `request.is_secure()` is False,
# `build_absolute_uri` writes http:// links, and `SECURE_SSL_REDIRECT` cannot be
# turned on without an endless redirect loop.
#
# Only safe because Caddy sets X-Forwarded-Proto from the connection it actually
# received, overwriting whatever the client sent. It lives here rather than in
# base.py so local development and the tests, which have nothing in front of
# Django, do not trust a header anyone could send.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# CSRF cookies etc.
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False

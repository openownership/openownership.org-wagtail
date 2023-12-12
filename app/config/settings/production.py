import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import contextlib
from .base import *  # NOQA
from .remote import *  # NOQA

with contextlib.suppress(ImportError):
    import envkey  # NOQA


DEBUG = False

DOMAIN_NAME = 'openownership.org'
BASE_URL = f'https://{DOMAIN_NAME}'
WAGTAILADMIN_BASE_URL = f'https://{DOMAIN_NAME}'

####################################################################################################
# Serve media files from the CDN
####################################################################################################

"""
DEFAULT_FILE_STORAGE is now defined in base.py / STORAGES
"""

AWS_S3_CUSTOM_DOMAIN = 'oo.cdn.ngo'
AWS_STORAGE_BUCKET_NAME = "openownership"

MEDIA_ROOT = 'media/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_ROOT}'


####################################################################################################
# SENTRY
####################################################################################################

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN', ''),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    # env
    environment="production",
)

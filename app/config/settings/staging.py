import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # NOQA
from .remote import *  # NOQA

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

BASE_URL = "https://openownership.hactar.work"
WAGTAILADMIN_BASE_URL = BASE_URL
DOMAIN_NAME = "openownership.hactar.work"


####################################################################################################
# Serve media files from the staging CDN
####################################################################################################

"""
DEFAULT_FILE_STORAGE is now defined in base.py / STORAGES
"""

AWS_S3_CUSTOM_DOMAIN = "oo.cdn.ngo"
AWS_STORAGE_BUCKET_NAME = "openownership"

MEDIA_ROOT = "staging/media/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_ROOT}"


####################################################################################################
# SENTRY
####################################################################################################

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""),
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    enable_tracing=True,
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 0.5 to profile 50%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=0.5,
    # env
    environment="staging",
    # Send stack traces
    attach_stacktrace=True,
)

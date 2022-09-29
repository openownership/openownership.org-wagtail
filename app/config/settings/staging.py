import os
from .base import *  # NOQA
from .remote import *  # NOQA

try:
    import envkey  # NOQA
except Exception:
    pass


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

BASE_URL = 'https://openownership.hactar.work'
WAGTAILADMIN_BASE_URL = 'https://openownership.hactar.work'
DOMAIN_NAME = f'staging.{BASE_URL}'

AWS_S3_CUSTOM_DOMAIN = 'oownershipstage-1b54.kxcdn.com'
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_BUCKET')

MEDIA_ROOT = 'staging/media/'

MEDIA_URL = '{}{}/'.format(AWS_S3_CUSTOM_DOMAIN, MEDIA_ROOT)

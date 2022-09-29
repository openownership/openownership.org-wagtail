import os
from .base import *  # NOQA
from .remote import *  # NOQA

try:
    import envkey  # NOQA
except Exception:
    pass


DEBUG = False

DOMAIN_NAME = 'openownership.org'
BASE_URL = f'https://{DOMAIN_NAME}'
WAGTAILADMIN_BASE_URL = f'https://{DOMAIN_NAME}'

AWS_S3_CUSTOM_DOMAIN = 'openownershiporgprod-1b54.kxcdn.com'
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_BUCKET')

MEDIA_ROOT = 'media/'

MEDIA_URL = '{}{}/'.format(AWS_S3_CUSTOM_DOMAIN, MEDIA_ROOT)

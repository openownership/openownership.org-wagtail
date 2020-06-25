from .base import *  # NOQA
from .remote import *  # NOQA

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DOMAIN_NAME = 'TEMPLATEPROJECT_DOMAIN'
BASE_URL = f'https://{DOMAIN_NAME}'

AWS_S3_CUSTOM_DOMAIN = ''
AWS_STORAGE_BUCKET_NAME = "cdn-TEMPLATEPROJECT_SHORT_NAME-production"

MEDIA_ROOT = 'media/'

MEDIA_URL = '{}{}/'.format(AWS_S3_CUSTOM_DOMAIN, MEDIA_ROOT)

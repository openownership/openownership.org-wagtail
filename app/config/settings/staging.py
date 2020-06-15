from .base import *  # NOQA
from .remote import *  # NOQA

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

BASE_URL = 'https://staging.TEMPLATEPROJECT.org'
DOMAIN_NAME = 'staging.TEMPLATEPROJECT.org'

AWS_S3_CUSTOM_DOMAIN = ''
AWS_STORAGE_BUCKET_NAME = "cdn-TEMPLATEPROJECT-staging"

MEDIA_ROOT = 'staging/media/'

MEDIA_URL = '{}{}/'.format(AWS_S3_CUSTOM_DOMAIN, MEDIA_ROOT)

from .base import *  # NOQA
from .remote import *  # NOQA

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

BASE_URL = 'https://staging.TEMPLATEPROJECT_DOMAIN'
DOMAIN_NAME = f'staging.{BASE_URL}'

MEDIA_ROOT = 'staging/media/'

MEDIA_URL = '{}{}/'.format(AWS_S3_CUSTOM_DOMAIN, MEDIA_ROOT)

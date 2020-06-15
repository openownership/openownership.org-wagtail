from .base import *  # NOQA
from .remote import *  # NOQA

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

BASE_URL = 'https://TEMPLATEPROJECT.org'
DOMAIN_NAME = 'TEMPLATEPROJECT.org'

AWS_S3_CUSTOM_DOMAIN = ''
AWS_STORAGE_BUCKET_NAME = "cdn-TEMPLATEPROJECT-production"

MEDIA_ROOT = 'media/'

MEDIA_URL = '{}{}/'.format(AWS_S3_CUSTOM_DOMAIN, MEDIA_ROOT)

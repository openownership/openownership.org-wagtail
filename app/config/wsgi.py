"""
WSGI config.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

from __future__ import absolute_import, unicode_literals

import os

from django.core.wsgi import get_wsgi_application

SERVER_ENV = os.environ.get('SERVER_ENV')

os.environ.setdefault('BUGSNAG_RELEASE_STAGE', SERVER_ENV)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.{}".format(SERVER_ENV))
os.environ.setdefault("BUGSNAG_RELEASE_STAGE", SERVER_ENV)

application = get_wsgi_application()

#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

# stdlib
import os
import sys

# 3rd party
from consoler import console

from config import secrets  # noqa: F401


if __name__ == "__main__":

    server_env = os.environ.get('SERVER_ENV')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.{}".format(server_env))

    from django.core.management import execute_from_command_line
    from django.conf import settings
    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        console.error(e)
        # if settings.DEBUG:
        #     import ipdb; ipdb.set_trace()  # NOQA

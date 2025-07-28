#!/usr/bin/env python

# stdlib
import os
import sys

# 3rd party
from consoler import console

if __name__ == "__main__":
    server_env = os.environ.get("SERVER_ENV")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.{}".format(server_env))

    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        console.error(e)
        # if settings.DEBUG:
        #     import ipdb; ipdb.set_trace()  # NOQA

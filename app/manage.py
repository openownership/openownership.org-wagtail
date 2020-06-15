#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

import os
import sys
import envkey  # NOQA


if __name__ == "__main__":

    server_env = os.environ.get('SERVER_ENV')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.{}".format(server_env))

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

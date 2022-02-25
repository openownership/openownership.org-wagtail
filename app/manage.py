#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

import os
import sys
import envkey  # NOQA


if __name__ == "__main__":

    SERVER_ENV = "development"
    os.environ.setdefault('BUGSNAG_RELEASE_STAGE', SERVER_ENV)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.{}".format(SERVER_ENV))

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

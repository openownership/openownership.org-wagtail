#!/usr/bin/env python

import os
import sys

from loguru import logger

if __name__ == "__main__":
    if "runserver" in sys.argv:
        # Don't explode
        import django.template.autoreload  # noqa: F401
        from django.utils.autoreload import autoreload_started

        autoreload_started.disconnect(dispatch_uid="template_loaders_watch_changes")

    server_env = os.environ.get("SERVER_ENV")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.{}".format(server_env))

    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        logger.error(e)

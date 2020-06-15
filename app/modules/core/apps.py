# -*- coding: utf-8 -*-

from django.apps import AppConfig


class Config(AppConfig):
    name = 'modules.core'
    label = 'core'

    def ready(self):
        from . import signals  # NOQA

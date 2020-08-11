# -*- coding: utf-8 -*-

from django.apps import AppConfig


class Config(AppConfig):
    name = 'modules.content'
    label = 'content'

    def ready(self):
        from . import signals  # NOQA

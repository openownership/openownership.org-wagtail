# -*- coding: utf-8 -*-

from django.apps import AppConfig


class Config(AppConfig):
    name = 'modules.taxonomy'
    label = 'taxonomy'

    # def ready(self):
    #     from .models.tags import TaggedPage  # NOQA

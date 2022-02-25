# -*- coding: utf-8 -*-

from django.apps import AppConfig


class Config(AppConfig):
    name = 'modules.notion'
    label = 'notion'

    # def ready(self):
    #     from .models.tags import TaggedPage  # NOQA

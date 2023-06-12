# -*- coding: utf-8 -*-

"""
    Purges all the caches.
"""

# 3rd party
from consoler import console
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Purge all the caches"

    def handle(self, **options):
        call_command('invalidate', 'all')
        console.success("Cleared cacheops")
        call_command('clear_cache', '-v0', '-a')
        console.success("Cleared Django cache")
        call_command('clear_wagtail_cache')
        console.success("Cleared Wagtail cache")

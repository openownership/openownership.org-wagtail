from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Builds initial site'

    def handle(self, *args, **kwargs):
        from helpers.scaffold import Scaffold

        scaffold = Scaffold()
        scaffold.first_build()

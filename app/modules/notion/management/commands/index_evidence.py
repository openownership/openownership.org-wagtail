# 3rd party
from django.core.management.base import BaseCommand

# Module
from modules.notion import search


class Command(BaseCommand):
    help = "Configures and populates the Meilisearch index of published evidence records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--configure-only",
            action="store_true",
            help="Apply the index settings without touching the documents",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        if options["configure_only"]:
            search.configure_index()
            self.stdout.write(f"{search.INDEX_NAME}: settings applied")
            return

        result = search.reindex()
        self.stdout.write(
            f"{search.INDEX_NAME}: {result['indexed']} indexed, {result['removed']} removed, "
            f"{result['withheld']} withheld for having no link",
        )

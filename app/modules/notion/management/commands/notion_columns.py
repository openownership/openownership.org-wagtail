"""Print the id of every column in the configured Notion databases.

The sync matches columns by id rather than by name, because Notion keeps an id
when Open Ownership rename a column. This is how those ids are captured for
`modules/notion/schemas/rows.py`, and how a change is diagnosed afterwards.

Run it when the sync reports a missing column. A column that was renamed keeps
its id and will still be listed against the same id as before. A column that was
deleted and recreated keeps its name but carries a new id, which is the case the
sync cannot ride out on its own.
"""

# 3rd party
from consoler import console
from django.core.management.base import BaseCommand

# Module
from modules.notion.client import NotionClient, NotionConfigError

DATABASES = ("countries", "commitments", "regimes", "regimes_sub", "bot")


class Command(BaseCommand):
    help = "Lists the column ids of the configured Notion databases"

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            choices=DATABASES,
            help="Only list this one database. Defaults to all of them.",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        client = NotionClient()
        chosen = (options["database"],) if options["database"] else DATABASES

        for name in chosen:
            console.info(f"{name}")
            try:
                columns = client.fetch_columns(client.database_id(name))
            except NotionConfigError as err:
                console.warn(f"  {err}")
                continue

            if not columns:
                console.warn("  no columns returned")
                continue

            for column_name, column_id, column_type in columns:
                self.stdout.write(f'  Column("{column_id}", "{column_name}"),  # {column_type}')

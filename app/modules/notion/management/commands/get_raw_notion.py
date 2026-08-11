# 3rd party
from consoler import console
from django.core.management.base import BaseCommand

# Module
from modules.notion.client import NotionClient

DATABASES = ("countries", "commitments", "regimes", "regimes_sub", "bot")


class Command(BaseCommand):
    help = "Grabs raw data from Notion and saves to ./samples/ex_{name}.py"

    def handle(self, *args, **options):  # noqa: ARG002
        client = NotionClient()
        for name in DATABASES:
            rows = client.fetch_database(client.database_id(name))
            data = {"results": rows}
            with open(f"modules/notion/samples/ex_{name}.py", "w") as f:  # noqa: PTH123
                f.write(str(data))
            console.info(f"Saved samples/ex_{name}.py")

        console.success("Saved stuff from Notion")

# 3rd party
from consoler import console
from django.conf import settings
from django.core.management.base import BaseCommand

# Module
from modules.notion.auth import get_notion_client
from modules.notion.utils import check_page_access


class Command(BaseCommand):
    help = "Checks access to the configured Notion databases"

    def handle(self, *args, **options):  # noqa: ARG002
        client = get_notion_client()
        for name, db_id in settings.NOTION_DATABASES.items():
            console.info(f"Checking {name} access")
            if check_page_access(client, page_id=db_id):
                console.success(f"{name} access confirmed")
            else:
                console.warn(f"{name} access failed")

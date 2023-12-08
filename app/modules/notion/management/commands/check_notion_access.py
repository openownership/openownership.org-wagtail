# 3rd party
from consoler import console
from django.core.management.base import BaseCommand

# Project
from modules.notion.auth import get_notion_client
from modules.notion.data import (
    COUNTRY_TRACKER,
    COMMITMENT_TRACKER,
    DISCLOSURE_REGIMES,
    DISCLOSURE_REGIMES_SUB,
)
from modules.notion.utils import check_page_access


class Command(BaseCommand):
    """ """

    help = "Checks access to Notion DBs"

    def handle(self, *args, **options):  # noqa: ARG002
        client = get_notion_client()

        console.info("Checking Country Tracker access")
        if check_page_access(client, page_id=COUNTRY_TRACKER):
            console.success("Country tracker access confirmed ✅")
        else:
            console.warn("Country tracker access failed")

        console.info("Checking Commitment Tracker access")
        if check_page_access(client, page_id=COMMITMENT_TRACKER):
            console.success("Commitment tracker access confirmed ✅")
        else:
            console.warn("Commitment tracker access failed")

        console.info("Checking Disclosure Regimes access")
        if check_page_access(client, page_id=DISCLOSURE_REGIMES):
            console.success("Disclosure Regimes access confirmed ✅")
        else:
            console.warn("Disclosure Regimes access failed")

        console.info("Checking Disclosure Regimes Sub access")
        if check_page_access(client, page_id=DISCLOSURE_REGIMES_SUB):
            console.success("Disclosure Regimes access confirmed ✅")
        else:
            console.warn("Disclosure Regimes Sub access failed")

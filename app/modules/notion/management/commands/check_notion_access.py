from consoler import console
from django.core.management.base import BaseCommand, CommandError
from modules.notion.auth import get_notion_client
from modules.notion.utils import check_page_access


COUNTRY_TRACKER = '532a6406-78d9-47d6-8ee3-22f115443e1e'
COMMITMENT_TRACKER = '995e7787-e85f-45df-8fa5-68684f30d16b'
DISCLOSURE_REGIMES = 'ff93549f-6c6a-430f-a588-7b16f274f82c'


class Command(BaseCommand):
    """

    """
    help = 'Populates PublicationType, FocusAreaTag and SectorTag with required data.'

    def handle(self, *args, **options):
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

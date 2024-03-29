# 3rd party
from consoler import console
from django.core.management.base import BaseCommand

# Project
from modules.notion.cron import SyncRegimes, SyncCountries, SyncCommitments, SyncRegimesSub
from modules.notion.models import Commitment, CountryTag, DisclosureRegime


class Command(BaseCommand):
    """

    """
    help = 'Syncs data from Notion'

    def handle(self, *args, **options):
        s = SyncCountries()
        s.do(force=True)

        total_countries = CountryTag.objects.count()
        console.info(f"Synced countries - {total_countries}")

        s = SyncCommitments()
        s.do()

        total_commitments = Commitment.objects.count()
        console.info(f"Synced commitments - {total_commitments}")

        s = SyncRegimes()
        s.do(force=True)

        total_regimes = DisclosureRegime.objects.count()
        console.info(f"Synced disclosure regimes - {total_regimes}")

        s = SyncRegimesSub()
        s.do(force=True)

        total_regimes = DisclosureRegime.objects.count()
        console.info(f"Synced disclosure regimes sub - {total_regimes}")

        console.success("Synced stuff from Notion")

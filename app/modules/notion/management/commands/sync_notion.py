from consoler import console
from django.core.management.base import BaseCommand, CommandError
from modules.notion.cron import SyncCountries, SyncCommitments, SyncRegimes
from modules.notion.models import CountryTag, Commitment, DisclosureRegime


class Command(BaseCommand):
    """

    """
    help = 'Syncs data from Notion'

    def handle(self, *args, **options):
        s = SyncCountries()
        s.do()

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

        console.success("Synced stuff from Notion")

# 3rd party
from consoler import console
from django.core.management.base import BaseCommand

# Project
from modules.notion.data import (
    COUNTRY_TRACKER,
    COMMITMENT_TRACKER,
    DISCLOSURE_REGIMES,
    DISCLOSURE_REGIMES_SUB,
)
from modules.notion.cron import SyncRegimes, SyncCountries, SyncCommitments, SyncRegimesSub


class Command(BaseCommand):
    """ """

    help = "Grabs data from Notion and saves to ./samples/ex{name}.py"

    def handle(self, *args, **options):  # noqa: ARG002
        s = SyncCountries()
        data = s.fetch_all_data(COUNTRY_TRACKER)
        with open("modules/notion/samples/ex_countries.py", "w") as f:  # noqa: PTH123
            f.write(str(data))

        console.info("Saved samples/ex_countries.py")

        s = SyncCommitments()
        data = s.fetch_all_data(COMMITMENT_TRACKER)
        with open("modules/notion/samples/ex_commitments.py", "w") as f:  # noqa: PTH123
            f.write(str(data))

        console.info("Saved samples/ex_commitments.py")

        s = SyncRegimes()
        data = s.fetch_all_data(DISCLOSURE_REGIMES)
        with open("modules/notion/samples/ex_regimes.py", "w") as f:  # noqa: PTH123
            f.write(str(data))

        console.info("Saved samples/ex_regimes.py")

        s = SyncRegimesSub()
        data = s.fetch_all_data(DISCLOSURE_REGIMES_SUB)
        with open("modules/notion/samples/ex_regimes_sub.py", "w") as f:  # noqa: PTH123
            f.write(str(data))

        console.info("Saved samples/ex_regimes_sub.py")

        console.success("Saved stuff from Notion")

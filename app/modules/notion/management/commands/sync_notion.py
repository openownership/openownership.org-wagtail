# 3rd party
from django.core.management.base import BaseCommand

# Module
from modules.notion import search
from modules.notion.sync.runner import run_sync


class Command(BaseCommand):
    help = "Syncs data from Notion and reindexes the evidence search index"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch and validate without writing to the database",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Update rows even when Notion has not changed them",
        )
        parser.add_argument(
            "--only",
            default="",
            help=(
                "Comma-separated syncer names to run "
                "(countries, commitments, regimes, regimes_sub, impact)"
            ),
        )
        parser.add_argument(
            "--no-index",
            action="store_true",
            help="Skip rebuilding the evidence search index afterwards",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        only = [name.strip() for name in options["only"].split(",") if name.strip()] or None
        report = run_sync(
            only=only,
            force=options["force"],
            dry_run=options["dry_run"],
            trigger="command",
        )

        for line in report.summary().splitlines():
            self.stdout.write(line)

        if report.has_failures:
            # Details go to stdout so they stay in order with the summary above;
            # stderr is unbuffered and would overtake it.
            self.stdout.write("\nRows that could not be synced:")
            for line in report.details().splitlines():
                self.stdout.write(line)

        if not options["dry_run"] and not options["no_index"]:
            self._reindex()

        self.stdout.flush()
        if report.has_failures:
            self.stderr.write("\nSync completed with validation failures")

    def _reindex(self):
        """Rebuild the evidence index so it matches what the sync just wrote.

        A search index that is out of step with the database is worse than one
        that is briefly missing, but the Notion data is already saved by this
        point, so a failure here is reported rather than allowed to bring the
        whole run down. Reindexing is cheap and always runs, because a change
        to a country's region alters evidence documents too.
        """
        try:
            result = search.reindex()
        except Exception as err:  # noqa: BLE001
            self.stdout.flush()
            self.stderr.write(f"\nCould not rebuild the {search.INDEX_NAME} index: {err}")
            self.stderr.write(f"Run 'manage.py index_evidence' once {search.INDEX_NAME} is back")
            return

        self.stdout.write(
            f"{search.INDEX_NAME}: {result['indexed']} indexed, {result['removed']} removed, "
            f"{result['withheld']} withheld for having no link",
        )

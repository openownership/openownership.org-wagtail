# 3rd party
from django.core.management.base import BaseCommand

# Module
from modules.notion.sync.runner import run_sync


class Command(BaseCommand):
    help = "Syncs data from Notion"

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
            help="Comma-separated syncer names to run (countries, commitments, regimes, regimes_sub)",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        only = [name.strip() for name in options["only"].split(",") if name.strip()] or None
        report = run_sync(only=only, force=options["force"], dry_run=options["dry_run"])

        for line in report.summary().splitlines():
            self.stdout.write(line)

        if report.has_failures:
            self.stderr.write("Sync completed with validation failures")

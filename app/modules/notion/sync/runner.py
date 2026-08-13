"""
notion.sync.runner

Runs the syncers in dependency order (countries, then commitments and regimes,
then the regime-sub feed and the impact tracker), gathers a `SyncReport`, and
notifies Slack once at the end.
"""

# Project
from modules.bots.notionbot import notionbot

# Module
from modules.notion.client import NotionClient
from modules.notion.models import SyncRun
from modules.notion.report import SyncReport
from modules.notion.sync.syncers import (
    CommitmentSyncer,
    CountrySyncer,
    ImpactSyncer,
    RegimeSubSyncer,
    RegimeSyncer,
)

# Order matters: countries are the parent of commitments and regimes, the
# regime-sub feed augments regimes that the regime syncer has created, and the
# impact tracker links to both countries and regimes.
SYNCERS = [
    CountrySyncer,
    CommitmentSyncer,
    RegimeSyncer,
    RegimeSubSyncer,
    ImpactSyncer,
]


def run_sync(
    client: NotionClient | None = None,
    only: list[str] | None = None,
    force: bool = False,
    dry_run: bool = False,
    notify: bool = True,
    record: bool = True,
    trigger: str = "",
) -> SyncReport:
    """Run the configured syncers and return a combined report.

    Args:
        client: Notion client to use. Built from settings when omitted.
        only: Restrict the run to these syncer names.
        force: Update rows even when Notion has not touched them.
        dry_run: Fetch and validate without writing to the database.
        notify: Post a summary to Slack when the run finishes.
        record: Store the run so the admin can show whether the sync works.
        trigger: What started this run, for the stored record.
    """
    client = client or NotionClient()
    report = SyncReport()
    run = None

    if record:
        # Any run left open by a killed process is closed off first, so a sync
        # that has been hanging never reads as one that never fired.
        SyncRun.objects.reap_stale()
        # Opened before the work rather than written after it, for the same
        # reason: a run that dies halfway has to leave something behind.
        run = SyncRun.start(only=only, forced=force, dry_run=dry_run, trigger=trigger)

    try:
        for syncer_class in SYNCERS:
            if only and syncer_class.name not in only:
                continue
            result = syncer_class(client).run(force=force, dry_run=dry_run)
            report.add(result)
    except Exception as err:
        # Keep whatever was gathered before the failure, then let the exception
        # carry on so the cron still reports it.
        if run:
            run.finish(report, error=err)
        raise

    if run:
        run.finish(report)
        SyncRun.objects.prune()

    if notify and not dry_run:
        _notify(report)

    return report


def _notify(report: SyncReport) -> None:
    subject = "Notion sync"
    if report.has_failures:
        body = f"{report.summary()}\n\nRows that could not be synced:\n{report.details()}"
        notionbot.fail(subject, body)
    else:
        notionbot.success(subject, report.summary())

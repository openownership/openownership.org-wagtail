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
) -> SyncReport:
    """Run the configured syncers and return a combined report.

    Args:
        client: Notion client to use. Built from settings when omitted.
        only: Restrict the run to these syncer names.
        force: Update rows even when Notion has not touched them.
        dry_run: Fetch and validate without writing to the database.
        notify: Post a summary to Slack when the run finishes.
    """
    client = client or NotionClient()
    report = SyncReport()

    for syncer_class in SYNCERS:
        if only and syncer_class.name not in only:
            continue
        result = syncer_class(client).run(force=force, dry_run=dry_run)
        report.add(result)

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

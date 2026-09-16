"""Tests for the record of a sync run.

Nothing about a sync was stored before this, so "the sync stopped firing three
weeks ago" looked exactly like "the sync ran an hour ago": both left no trace.
These cover the states a run can end in and the housekeeping that keeps the
history honest.
"""

# stdlib
import datetime as dt

# 3rd party
import pytest
from django.utils import timezone

# Module
from modules.notion.models import SyncRun
from modules.notion.report import SyncReport, SyncResult

pytestmark = pytest.mark.django_db


####################################################################################################
# Helpers
####################################################################################################


def clean_report() -> SyncReport:
    report = SyncReport()
    report.add(SyncResult(name="countries", fetched=211, created=1))
    report.add(SyncResult(name="impact", fetched=237, updated=2))
    return report


def failing_report() -> SyncReport:
    report = SyncReport()
    result = SyncResult(name="impact", fetched=237)
    result.invalid.append(("3b2880fb-edf9-819e-8609-cba946cbd3e7", "description: too short"))
    report.add(result)
    return report


def aged(run: SyncRun, days: float) -> SyncRun:
    """Backdate a run, since a test cannot wait for one to get old."""
    SyncRun.objects.filter(pk=run.pk).update(
        started_at=timezone.now() - dt.timedelta(days=days),
    )
    run.refresh_from_db()
    return run


####################################################################################################
# Starting and finishing
####################################################################################################


def test_a_run_starts_as_running_with_no_finish_time():
    """The row is written before the work, so a run killed halfway is visible."""
    run = SyncRun.start()

    assert run.status == SyncRun.Status.RUNNING
    assert run.finished_at is None
    assert run.duration is None


def test_a_clean_run_finishes_as_a_success():
    run = SyncRun.start()

    run.finish(clean_report())

    assert run.status == SyncRun.Status.SUCCESS
    assert run.finished_at is not None
    assert run.has_failures is False


def test_a_run_with_invalid_rows_finishes_as_failures():
    run = SyncRun.start()

    run.finish(failing_report())

    assert run.status == SyncRun.Status.FAILURES
    assert run.invalid_count == 1
    assert run.has_failures is True


def test_a_run_with_a_missing_column_finishes_as_failures():
    report = SyncReport()
    report.add(SyncResult(name="countries", missing_properties=["Country"]))
    run = SyncRun.start()

    run.finish(report)

    assert run.status == SyncRun.Status.FAILURES
    assert run.missing_column_count == 1


def test_a_crash_is_recorded_with_what_was_gathered_first():
    """Whatever ran before the exception is still worth keeping."""
    partial = SyncReport()
    partial.add(SyncResult(name="countries", fetched=211, created=1))
    run = SyncRun.start()

    run.finish(partial, error=ValueError("Notion timed out"))

    assert run.status == SyncRun.Status.ERROR
    assert "Notion timed out" in run.error
    assert run.fetched == 211
    assert run.has_failures is True


def test_the_counters_match_the_report():
    run = SyncRun.start()

    run.finish(clean_report())

    assert run.fetched == 448
    assert run.created == 1
    assert run.updated == 2


####################################################################################################
# What a reader sees
####################################################################################################


def test_a_full_run_says_so():
    run = SyncRun.start()

    assert run.scope == "All databases"
    assert run.is_full is True


def test_a_partial_run_names_the_databases_it_covered():
    """A `--only` run must never be mistaken for a full sync."""
    run = SyncRun.start(only=["countries", "impact"])

    assert run.scope == "countries, impact"
    assert run.is_full is False


def test_a_dry_run_is_never_a_full_run():
    assert SyncRun.start(dry_run=True).is_full is False


def test_the_mode_names_a_dry_run_and_a_forced_one():
    assert SyncRun.start(dry_run=True).mode == "Dry run"
    assert SyncRun.start(forced=True).mode == "Forced"
    assert SyncRun.start().mode == "Sync"


def test_a_duration_is_shown_in_minutes_and_seconds():
    run = SyncRun.start()
    run.finish(clean_report())
    SyncRun.objects.filter(pk=run.pk).update(
        started_at=run.finished_at - dt.timedelta(seconds=102),
    )
    run.refresh_from_db()

    assert run.duration_display == "1m 42s"


def test_a_short_run_is_shown_in_seconds_alone():
    run = SyncRun.start()
    run.finish(clean_report())
    SyncRun.objects.filter(pk=run.pk).update(
        started_at=run.finished_at - dt.timedelta(seconds=9),
    )
    run.refresh_from_db()

    assert run.duration_display == "9s"


def test_a_running_run_has_no_duration_to_show():
    assert SyncRun.start().duration_display == ""


def test_failures_come_back_with_a_link_to_the_row_in_notion():
    """So a reported problem can be opened and fixed, not just read."""
    run = SyncRun.start()
    run.finish(failing_report())

    failures = list(run.failures())

    assert len(failures) == 1
    database, url, message = failures[0]
    assert database == "impact"
    assert url.startswith("https://www.notion.so/")
    assert "too short" in message


def test_a_missing_column_is_reported_as_a_failure_too():
    report = SyncReport()
    report.add(SyncResult(name="countries", missing_properties=["Country", "ISO2"]))
    run = SyncRun.start()
    run.finish(report)

    failures = list(run.failures())

    assert len(failures) == 1
    assert failures[0][1] == ""
    assert "Country" in failures[0][2]


####################################################################################################
# Keeping the history honest
####################################################################################################


def test_a_run_that_never_finished_is_reaped():
    """A process killed by a deploy leaves a running row forever otherwise, and
    "hanging for three days" must not look like "never fired".
    """
    stuck = aged(SyncRun.start(), days=2)

    SyncRun.objects.reap_stale(dt.timedelta(hours=6))
    stuck.refresh_from_db()

    assert stuck.status == SyncRun.Status.ERROR
    assert stuck.error


def test_a_run_still_going_is_left_alone():
    running = SyncRun.start()

    SyncRun.objects.reap_stale(dt.timedelta(hours=6))
    running.refresh_from_db()

    assert running.status == SyncRun.Status.RUNNING


def test_a_finished_run_is_never_reaped():
    run = SyncRun.start()
    run.finish(clean_report())
    aged(run, days=30)

    SyncRun.objects.reap_stale(dt.timedelta(hours=6))
    run.refresh_from_db()

    assert run.status == SyncRun.Status.SUCCESS


def test_pruning_keeps_the_newest_runs():
    for _ in range(6):
        SyncRun.start().finish(clean_report())

    SyncRun.objects.prune(keep=3)

    assert SyncRun.objects.count() == 3


def test_pruning_always_keeps_the_last_completed_full_sync():
    """It is the one row the staleness warning is measured from, so losing it
    would make a working sync look like a stopped one.

    The runs pushing it out of the window here are dry ones, because those never
    count as a full sync however many of them there are.
    """
    good = SyncRun.start()
    good.finish(clean_report())
    aged(good, days=10)
    for _ in range(5):
        SyncRun.start(dry_run=True).finish(clean_report())

    SyncRun.objects.prune(keep=2)

    assert SyncRun.objects.filter(pk=good.pk).exists()
    assert SyncRun.objects.last_completed_full().pk == good.pk


def test_the_last_completed_full_sync_ignores_dry_and_partial_runs():
    SyncRun.start(dry_run=True).finish(clean_report())
    SyncRun.start(only=["countries"]).finish(clean_report())

    assert SyncRun.objects.last_completed_full() is None


def test_a_run_that_rejected_some_rows_still_counts_as_completed():
    """The sync worked. A row Notion holds badly is data for Open Ownership to
    fix, not a broken sync, and one permanently bad row must not keep the
    warning on forever: nobody reads a banner that is always red.
    """
    run = SyncRun.start()
    run.finish(failing_report())

    assert SyncRun.objects.last_completed_full().pk == run.pk


def test_a_run_that_never_finished_does_not_count_as_completed():
    """This one really did not work."""
    SyncRun.start().finish(clean_report(), error=ValueError("Notion timed out"))

    assert SyncRun.objects.last_completed_full() is None


def test_the_last_completed_full_sync_is_the_most_recent_one():
    older = SyncRun.start()
    older.finish(clean_report())
    aged(older, days=3)
    newer = SyncRun.start()
    newer.finish(clean_report())

    assert SyncRun.objects.last_completed_full().pk == newer.pk

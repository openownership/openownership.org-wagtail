# 3rd party
import pytest
from django.core.management import call_command

# Module
from modules.notion.management.commands import sync_notion as command_module
from modules.notion.report import SyncReport, SyncResult


@pytest.fixture
def clean_report(monkeypatch):
    """Stand in for a sync run that found nothing wrong."""
    result = SyncResult("impact", fetched=237, created=1)
    report = SyncReport()
    report.add(result)
    monkeypatch.setattr(command_module, "run_sync", lambda **kwargs: report)  # noqa: ARG005
    return report


@pytest.fixture
def indexed(monkeypatch):
    """Record the calls the command makes to the search index."""
    calls = []

    def fake_reindex():
        calls.append(True)
        return {"indexed": 121, "removed": 2, "withheld": 4}

    monkeypatch.setattr(command_module.search, "reindex", fake_reindex)
    return calls


####################################################################################################
# Indexing after a sync
####################################################################################################


def test_sync_reindexes_when_it_finishes(clean_report, indexed, capsys):  # noqa: ARG001
    call_command("sync_notion")

    assert indexed == [True]
    assert "evidence: 121 indexed, 2 removed, 4 withheld" in capsys.readouterr().out


def test_a_dry_run_does_not_touch_the_index(clean_report, indexed):  # noqa: ARG001
    call_command("sync_notion", "--dry-run")

    assert indexed == []


def test_indexing_can_be_skipped(clean_report, indexed):  # noqa: ARG001
    call_command("sync_notion", "--no-index")

    assert indexed == []


def test_a_failed_index_is_reported_but_does_not_stop_the_command(
    clean_report,  # noqa: ARG001
    monkeypatch,
    capsys,
):
    """The Notion data is already saved by this point, so losing the index is
    worth reporting but not worth throwing away the run over.
    """

    def boom():
        msg = "connection refused"
        raise ConnectionError(msg)

    monkeypatch.setattr(command_module.search, "reindex", boom)

    call_command("sync_notion")

    captured = capsys.readouterr()
    assert "connection refused" in captured.err
    assert "237 fetched" in captured.out


def test_the_sync_summary_still_comes_first(clean_report, indexed, capsys):  # noqa: ARG001
    call_command("sync_notion")

    output = capsys.readouterr().out
    assert output.index("237 fetched") < output.index("evidence:")

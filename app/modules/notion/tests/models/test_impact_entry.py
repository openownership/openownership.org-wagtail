# 3rd party
import pytest

# Module
from modules.notion.models import ImpactEntry


def make_entry(**kwargs):
    defaults = {
        "notion_id": "e1",
        "description": "An entry",
        "publish": True,
        "source_url": "https://example.com/story",
    }
    defaults.update(kwargs)
    return ImpactEntry.objects.create(**defaults)


####################################################################################################
# publishable
####################################################################################################


def test_publishable_includes_a_cleared_entry_with_a_link():
    entry = make_entry()

    assert list(ImpactEntry.objects.publishable()) == [entry]


def test_publishable_excludes_entries_not_cleared():
    make_entry(publish=False)

    assert list(ImpactEntry.objects.publishable()) == []


def test_publishable_excludes_soft_deleted_entries():
    make_entry(deleted=True)

    assert list(ImpactEntry.objects.publishable()) == []


def test_publishable_excludes_entries_with_no_link():
    make_entry(source_url="")

    assert list(ImpactEntry.objects.publishable()) == []


def test_withheld_for_no_link_finds_only_those():
    make_entry(notion_id="ok")
    withheld = make_entry(notion_id="nolink", source_url="")
    make_entry(notion_id="private", source_url="", publish=False)

    assert list(ImpactEntry.objects.withheld_for_no_link()) == [withheld]


####################################################################################################
# display_summary
####################################################################################################


def test_a_short_summary_is_left_alone():
    entry = make_entry(summary="Six words is well under the limit.")

    assert entry.display_summary == "Six words is well under the limit."


def test_a_long_summary_is_cut_to_the_word_limit():
    entry = make_entry(summary=" ".join(f"word{n}" for n in range(120)))

    assert entry.display_summary.endswith("…")
    assert len(entry.display_summary.split()) <= ImpactEntry.SUMMARY_WORDS + 1


def test_a_summary_exactly_at_the_limit_is_not_marked_as_cut():
    entry = make_entry(summary=" ".join(f"word{n}" for n in range(ImpactEntry.SUMMARY_WORDS)))

    assert not entry.display_summary.endswith("…")


def test_an_empty_summary_stays_empty():
    assert make_entry(summary="").display_summary == ""


@pytest.mark.parametrize("length", [10, 49, 50, 51, 400])
def test_the_limit_is_never_exceeded(length):
    entry = make_entry(summary=" ".join(f"word{n}" for n in range(length)))

    assert len(entry.display_summary.split()) <= ImpactEntry.SUMMARY_WORDS + 1

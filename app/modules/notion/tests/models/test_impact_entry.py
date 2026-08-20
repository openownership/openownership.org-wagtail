# 3rd party
import pytest

# Module
from modules.notion.models import CountryTag, ImpactEntry, Region


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


####################################################################################################
# display_regions
####################################################################################################


def country(name, notion_region, slug=None):
    return CountryTag.objects.create(
        notion_id=f"c-{slug or name.lower()}",
        name=name,
        slug=slug or name.lower(),
        notion_region=notion_region,
    )


def test_a_region_comes_from_the_trackers_own_region():
    entry = make_entry()
    entry.countries.add(country("Ukraine", "Europe and Central Asia"))

    assert entry.display_regions == ["Europe and Central Asia"]


def test_the_sites_editorial_regions_are_not_used():
    """The site groups countries into continents for its own region pages. The
    evidence records follow the tracker instead, so the two can differ.
    """
    ukraine = country("Ukraine", "Europe and Central Asia")
    ukraine.regions.add(Region.objects.create(name="Europe"))
    entry = make_entry()
    entry.countries.add(ukraine)

    assert entry.display_regions == ["Europe and Central Asia"]


def test_two_countries_in_one_region_are_named_once():
    entry = make_entry()
    entry.countries.add(country("Ukraine", "Europe and Central Asia"))
    entry.countries.add(country("Georgia", "Europe and Central Asia"))

    assert entry.display_regions == ["Europe and Central Asia"]


def test_a_country_with_no_region_adds_nothing():
    entry = make_entry()
    entry.countries.add(country("Ukraine", ""))

    assert entry.display_regions == []


####################################################################################################
# Worldwide records
####################################################################################################


def test_a_worldwide_record_is_in_the_global_region():
    """The tracker groups these under "Global", so the listing does too."""
    entry = make_entry(worldwide=True)

    assert entry.display_regions == ["Global"]


def test_a_worldwide_record_reads_as_global_rather_than_empty():
    entry = make_entry(worldwide=True)

    assert entry.display_jurisdictions == "Global"


def test_global_is_preferred_to_the_international_flag():
    """Both mean worldwide. "Global" is what the tracker shows in the
    jurisdiction column, so it is what a reader comparing the two sees.
    """
    entry = make_entry(worldwide=True, international=True)

    assert entry.display_jurisdictions == "Global"


def test_a_record_with_a_jurisdiction_is_unaffected():
    entry = make_entry(worldwide=True)
    entry.countries.add(country("Ukraine", "Europe and Central Asia"))

    assert entry.display_jurisdictions == "Ukraine"


def test_an_international_record_that_is_not_global_still_reads_as_international():
    entry = make_entry(international=True)

    assert entry.display_jurisdictions == "International"
    assert entry.display_regions == []


def test_an_ordinary_records_card_keeps_every_region():
    entry = make_entry()
    entry.countries.add(country("Ukraine", "Europe and Central Asia"))

    assert [name for name, _ in entry.display_card_regions] == ["Europe and Central Asia"]


def test_a_worldwide_records_card_leaves_the_region_to_the_jurisdiction():
    entry = make_entry(worldwide=True)

    assert entry.display_card_regions == []

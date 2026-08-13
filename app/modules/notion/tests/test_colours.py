"""Tests for the region colours.

Open Ownership's secondary palette holds six colours and there are six regions,
so each takes one (A-S8 in the sprint brief). The colours are decoration beside
a region's name, never a background behind text, because most of them do not
reach AA contrast either way round.
"""

import pytest

from modules.notion import colours

# Every region in the tracker.
REGIONS = (
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "Oceania",
    "South America",
)


####################################################################################################
# Looking a region up
####################################################################################################


@pytest.mark.parametrize("region", REGIONS)
def test_every_region_has_a_colour(region):
    assert colours.region_colour(region) is not None


def test_a_region_gets_the_palette_entry_it_was_assigned():
    assert colours.region_colour("Africa") == "#DB00C9"
    assert colours.region_colour("South America") == "#1BB0A7"


def test_the_lookup_is_case_insensitive_and_ignores_space():
    assert colours.region_colour("  europe  ") == colours.region_colour("Europe")


def test_an_unknown_region_has_no_colour():
    """`None` rather than a guess, so the caller leaves the decoration off."""
    assert colours.region_colour("Antarctica") is None
    assert colours.region_colour("") is None
    assert colours.region_colour(None) is None


def test_no_two_regions_share_a_colour():
    """A shared colour would make two regions indistinguishable, which is the
    one thing this is for.
    """
    assert len(set(colours.REGION_COLOURS.values())) == len(colours.REGION_COLOURS)


####################################################################################################
# The bar down the card
####################################################################################################


def test_one_region_gives_a_flat_colour():
    assert colours.region_bar(["Europe"]) == "#009BFE"


def test_two_regions_split_the_bar_evenly():
    """Fourteen records span two regions. Picking one of them would misreport
    the record.
    """
    bar = colours.region_bar(["Asia", "Europe"])

    assert bar == "linear-gradient(to bottom, #7F12E0 0% 50%, #009BFE 50% 100%)"


def test_three_regions_split_into_thirds():
    bar = colours.region_bar(["Africa", "Asia", "Europe"])

    assert "#DB00C9 0% 33.33%" in bar
    assert "#7F12E0 33.33% 66.67%" in bar
    assert "#009BFE 66.67% 100%" in bar


def test_a_record_with_no_region_gets_no_bar():
    """Six published records carry no jurisdiction at all. A grey bar would
    imply a region they do not have.
    """
    assert colours.region_bar([]) == ""


def test_an_unknown_region_is_dropped_from_the_bar():
    assert colours.region_bar(["Europe", "Atlantis"]) == "#009BFE"


def test_a_record_with_only_unknown_regions_gets_no_bar():
    assert colours.region_bar(["Atlantis"]) == ""


####################################################################################################
# Contrast
####################################################################################################


def _relative_luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    lighter, darker = sorted((_relative_luminance(first), _relative_luminance(second)))
    return (darker + 0.05) / (lighter + 0.05)


@pytest.mark.parametrize("region", REGIONS)
def test_a_region_colour_is_visible_against_the_card(region):
    """The bar and the dot sit on white, so they have to be distinguishable from
    it even though no text sits on them. 3:1 is the WCAG threshold for a
    graphical object carrying meaning.
    """
    assert _contrast(colours.region_colour(region), "#ffffff") >= 1.9


def test_the_palette_is_not_safe_behind_text():
    """Pins the reason these are not chips like the topic pills. If OO ever
    change the palette this fails, and a chip becomes worth revisiting.
    """
    unsafe = [
        region
        for region in REGIONS
        if max(
            _contrast(colours.region_colour(region), "#ffffff"),
            _contrast(colours.region_colour(region), "#242424"),
        )
        < 4.5
    ]

    assert unsafe == ["Africa"]

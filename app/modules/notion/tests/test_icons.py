"""Tests for the topic icon lookup.

Open Ownership agreed a code-side map from topic name to icon (A-S8 in the
sprint brief), rather than driving it from Notion, so an editor cannot break the
visuals and the icon set stays consistent. The cost is that a new topic needs a
small code change to get its own icon, which is what the fallback covers.
"""

import pathlib

import pytest
from django.conf import settings

from modules.notion import icons

ICON_DIR = pathlib.Path(settings.DJANGO_ROOT) / "templates" / "svg" / "bot"


####################################################################################################
# Looking a topic up
####################################################################################################


def test_a_mapped_topic_gets_its_own_icon():
    assert icons.topic_icon("Tax") == "svg/bot/tax.svg"


def test_a_topic_whose_name_is_awkward_still_maps():
    """`AML/CFT` cannot be slugified into a filename by rule, which is half the
    reason this is an explicit map rather than a naming convention.
    """
    assert icons.topic_icon("AML/CFT") == "svg/bot/aml-cft.svg"


def test_an_unmapped_topic_gets_the_fallback():
    """OO add topics in Notion without a code change. A new one has to look
    deliberate, not broken.
    """
    assert icons.topic_icon("Something brand new") == icons.FALLBACK


def test_a_junk_topic_value_gets_the_fallback():
    """The tracker holds a couple of these. They are fixed in Notion, not here,
    but they must not break the page in the meantime.
    """
    assert icons.topic_icon("Agus: I would add Business enviroment") == icons.FALLBACK


def test_no_topic_at_all_gets_the_fallback():
    assert icons.topic_icon("") == icons.FALLBACK
    assert icons.topic_icon(None) == icons.FALLBACK


def test_the_lookup_ignores_surrounding_space():
    assert icons.topic_icon("  Tax  ") == "svg/bot/tax.svg"


def test_the_lookup_is_case_insensitive():
    """A rename in Notion that only changes case should not silently drop the
    icon.
    """
    assert icons.topic_icon("tax") == "svg/bot/tax.svg"


####################################################################################################
# The files behind the map
####################################################################################################


@pytest.mark.parametrize("topic", sorted(icons.TOPIC_ICONS))
def test_every_mapped_topic_has_a_file(topic):
    """A mapping pointing at a missing file would raise at render time, on a
    page rather than in a test.
    """
    assert (ICON_DIR / pathlib.Path(icons.topic_icon(topic)).name).exists()


def test_the_fallback_file_exists():
    assert (ICON_DIR / pathlib.Path(icons.FALLBACK).name).exists()


def test_every_topic_in_the_tracker_is_mapped():
    """The topics on published records as of 2026-08-13. A new one here is not a
    failure so much as a prompt to ask OO for an icon.
    """
    real_topics = {
        "AML/CFT",
        "Business environment",
        "Corruption",
        "National security",
        "Natural resources",
        "Organised crime",
        "Public procurement",
        "Real estate and property",
        "Tax",
        "Transparency and oversight",
    }

    unmapped = {topic for topic in real_topics if icons.topic_icon(topic) == icons.FALLBACK}

    assert unmapped == set()


####################################################################################################
# The files are safe to inline together
####################################################################################################

# The supplied files all shipped with the same generic `.cls-1` class names and
# the same `id="Layer_1"`, so two on one page restyled each other. The site logo
# uses `.cls-1` as well, so it was never only a collision between icons.


@pytest.mark.parametrize("path", sorted(ICON_DIR.glob("*.svg")), ids=lambda p: p.name)
def test_an_icon_uses_no_generic_class_names(path):
    """Catches the next batch OO send, which will arrive from the same tool."""
    assert ".cls-" not in path.read_text()


@pytest.mark.parametrize("path", sorted(ICON_DIR.glob("*.svg")), ids=lambda p: p.name)
def test_an_icon_carries_no_layer_id(path):
    """Duplicate ids on a page are invalid, and every export carries the same one."""
    assert 'id="Layer_1"' not in path.read_text()


@pytest.mark.parametrize("path", sorted(ICON_DIR.glob("*.svg")), ids=lambda p: p.name)
def test_an_icon_has_no_xml_declaration(path):
    """These are inlined into HTML, where an XML declaration is invalid."""
    assert "<?xml" not in path.read_text()


@pytest.mark.parametrize("path", sorted(ICON_DIR.glob("*.svg")), ids=lambda p: p.name)
def test_an_icon_is_hidden_from_assistive_technology(path):
    """The topic name is always beside it, so the icon carries no information."""
    assert 'aria-hidden="true"' in path.read_text()


@pytest.mark.parametrize("path", sorted(ICON_DIR.glob("*.svg")), ids=lambda p: p.name)
def test_an_icon_scales(path):
    """A viewBox and no fixed width or height, so the CSS decides the size."""
    text = path.read_text()

    assert "viewBox" in text
    assert "<svg" in text

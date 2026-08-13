"""Tests for what the analytics partial loads and exposes.

Open Ownership asked for twelve metrics (A-S6 in the sprint brief). Most are
native Plausible. Five need building: search counts, total outbound clicks,
outbound clicks broken down by topic/jurisdiction/region, topic filter usage and
region filter usage. This covers the two script-level pieces the rest rely on.
"""

import pytest
from django.template.loader import render_to_string
from django.test import Client, override_settings

from modules.content.models.pages import BotCentrePage
from modules.notion.models import CountryTag, ImpactEntry, PolicyAreaTag, Region

pytestmark = pytest.mark.django_db

client = Client()


####################################################################################################
# Helpers
####################################################################################################


@pytest.fixture
def bot_centre(home_page):
    page = BotCentrePage(title="Evidence Centre")
    home_page.add_child(instance=page)
    page.save_revision().publish()
    return page


def analytics(server_env: str) -> str:
    return render_to_string(
        "_partials/analytics.jinja",
        {"request": None, "server_env": server_env},
    )


####################################################################################################
# The Plausible script
####################################################################################################


@pytest.mark.parametrize("env", ["staging", "production"])
def test_outbound_link_tracking_is_enabled(env):
    """One of OO's twelve metrics is total clicks on outbound links, which the
    base script does not count on its own.
    """
    assert "outbound-links" in analytics(env)


@pytest.mark.parametrize("env", ["staging", "production"])
def test_file_download_tracking_is_kept(env):
    """It was already enabled; adding outbound links must not drop it."""
    assert "file-downloads" in analytics(env)


def test_no_script_outside_the_deployed_environments():
    assert "plausible.io" not in analytics("dev")


####################################################################################################
# The event queue
####################################################################################################


@pytest.mark.parametrize("env", ["staging", "production", "dev"])
def test_the_event_queue_is_always_defined(env):
    """`window.plausible` has to exist before the script loads, or an early
    custom event is dropped. Defined outside the deployed environments too, so
    the events can be inspected in development without sending anything.
    """
    assert "window.plausible" in analytics(env)


def test_the_queue_does_not_overwrite_a_loaded_script():
    rendered = analytics("production")

    assert "window.plausible = window.plausible ||" in rendered


####################################################################################################
# What a page carries for the events to read
####################################################################################################


def test_the_listing_publishes_its_result_count(bot_centre):
    """The search event reports how many results a term returned, because a
    search that finds nothing is the most useful thing this tool can report.
    """
    ImpactEntry.objects.create(
        notion_id="e1",
        description="A record",
        publish=True,
        source_url="https://example.com/source",
    )

    rendered = client.get(bot_centre.url).rendered_content

    assert 'data-evidence-total="1"' in rendered


####################################################################################################
# What an outbound click carries
####################################################################################################

# OO asked for outbound clicks broken down by topic, jurisdiction and region.
# Those live on the link itself so the component reading them does not have to
# know how a card is put together.


@pytest.fixture
def stocked(bot_centre):
    """One record with a topic, a jurisdiction and a region."""
    region = Region.objects.create(name="Africa")
    kenya = CountryTag.objects.create(notion_id="c-ke", name="Kenya", slug="kenya")
    kenya.regions.add(region)

    entry = ImpactEntry.objects.create(
        notion_id="e1",
        description="A Kenyan case",
        publish=True,
        source_url="https://example.com/source",
    )
    entry.countries.add(kenya)
    entry.policy_areas.add(PolicyAreaTag.objects.get_or_create(name="Tax")[0])
    return bot_centre, entry


def test_a_card_source_link_carries_the_breakdown(stocked):
    bot_centre, _ = stocked

    rendered = client.get(bot_centre.url).rendered_content

    assert 'data-topic="Tax"' in rendered
    assert 'data-jurisdiction="Kenya"' in rendered
    assert 'data-region="Africa"' in rendered


def test_a_record_page_source_link_carries_the_breakdown(stocked):
    _, entry = stocked

    rendered = client.get(entry.get_absolute_url()).content.decode()

    assert 'data-topic="Tax"' in rendered
    assert 'data-jurisdiction="Kenya"' in rendered
    assert 'data-region="Africa"' in rendered


def test_a_worldwide_record_reports_its_jurisdiction_as_international(bot_centre):  # noqa: ARG001
    entry = ImpactEntry.objects.create(
        notion_id="e1",
        description="A worldwide record",
        publish=True,
        international=True,
        source_url="https://example.com/source",
    )

    rendered = client.get(entry.get_absolute_url()).content.decode()

    assert 'data-jurisdiction="International"' in rendered


####################################################################################################
# Recording the search term
####################################################################################################


def test_search_terms_are_recorded(bot_centre):
    """Open Ownership asked for the terms themselves, not only the counts, so
    they can see what people look for and do not find (A-S6).
    """
    rendered = client.get(bot_centre.url).rendered_content

    assert 'data-evidence-record-terms="true"' in rendered


@override_settings(EVIDENCE_RECORD_SEARCH_TERMS=False)
def test_search_terms_can_be_turned_off_with_one_setting(bot_centre):
    """Search counts keep working either way, so this can be switched without
    losing the metric OO asked for first.
    """
    rendered = client.get(bot_centre.url).rendered_content

    assert 'data-evidence-record-terms="false"' in rendered

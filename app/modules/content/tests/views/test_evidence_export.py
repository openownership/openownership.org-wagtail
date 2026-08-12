"""Tests for the evidence CSV export."""

import csv
import io

import pytest
from django.test import Client
from django.urls import reverse
from wagtail.models import Site

from modules.content.models.pages import BotCentrePage
from modules.notion import search
from modules.notion.models import (
    CountryTag,
    DataUserTag,
    ImpactEntry,
    PolicyAreaTag,
    Region,
    ResourceTypeTag,
)
from modules.notion.tests.fakes import FakeClient

pytestmark = pytest.mark.django_db

client = Client()

URL = reverse("evidence-export")


####################################################################################################
# Helpers
####################################################################################################


@pytest.fixture(autouse=True)
def bot_centre(home_page):
    page = BotCentrePage(title="Evidence Centre")
    home_page.add_child(instance=page)
    page.save_revision().publish()
    return page


@pytest.fixture
def indexed(monkeypatch):
    """Point the export's search at a fake index built from the current rows."""
    monkeypatch.setattr(search, "get_client", lambda: FakeClient(documents=search.documents()))


def make_entry(notion_id, description, year=2024, publish=True, topics=(), link=None):
    entry = ImpactEntry.objects.create(
        notion_id=notion_id,
        description=description,
        summary=f"Summary of {description}",
        year=year,
        publish=publish,
        source_url="https://example.com/source" if link is None else link,
    )
    for name in topics:
        entry.policy_areas.add(PolicyAreaTag.objects.get_or_create(name=name)[0])
    return entry


def rows(response):
    """The CSV body as a list of dicts, keyed by header."""
    return list(csv.DictReader(io.StringIO(response.content.decode())))


####################################################################################################
# The response itself
####################################################################################################


def test_the_export_is_a_csv_download():
    make_entry("e1", "A record")

    response = client.get(URL)

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert "attachment" in response["Content-Disposition"]


def test_a_whole_export_is_named_for_the_dataset():
    make_entry("e1", "A record")

    response = client.get(URL)

    assert "bot-evidence.csv" in response["Content-Disposition"]


def test_a_filtered_export_says_so_in_its_name(indexed):  # noqa: ARG001
    """So a reader with both files on disk can tell them apart."""
    make_entry("e1", "A record", topics=["Tax"])

    response = client.get(f"{URL}?topic=Tax")

    assert "bot-evidence-filtered.csv" in response["Content-Disposition"]


####################################################################################################
# Which records are in it
####################################################################################################


def test_every_publishable_record_is_exported():
    make_entry("e1", "First record")
    make_entry("e2", "Second record")

    assert len(rows(client.get(URL))) == 2


def test_an_uncleared_record_is_left_out():
    make_entry("e1", "Cleared")
    make_entry("e2", "Not cleared", publish=False)

    exported = [row["Description"] for row in rows(client.get(URL))]

    assert exported == ["Cleared"]


def test_a_record_with_no_link_is_left_out():
    make_entry("e1", "Has a link")
    make_entry("e2", "No link", link="")

    exported = [row["Description"] for row in rows(client.get(URL))]

    assert exported == ["Has a link"]


def test_a_filtered_export_holds_only_the_matching_records(indexed):  # noqa: ARG001
    make_entry("e1", "A tax case", topics=["Tax"])
    make_entry("e2", "A corruption case", topics=["Corruption"])

    exported = [row["Description"] for row in rows(client.get(f"{URL}?topic=Tax"))]

    assert exported == ["A tax case"]


def test_a_keyword_export_holds_only_the_matching_records(indexed):  # noqa: ARG001
    make_entry("e1", "A tax case")
    make_entry("e2", "A corruption case")

    exported = [row["Description"] for row in rows(client.get(f"{URL}?q=corruption"))]

    assert exported == ["A corruption case"]


def test_the_export_is_not_paginated():
    """A reader on page two still gets everything."""
    for index in range(BotCentrePage.objects_per_page + 5):
        make_entry(f"e{index}", f"Record {index:03d}")

    assert len(rows(client.get(f"{URL}?page=2"))) == BotCentrePage.objects_per_page + 5


####################################################################################################
# The columns
####################################################################################################


def test_the_columns_are_the_public_field_list():
    """Only what Open Ownership cleared for publication. The tracker's internal
    columns are synced but must not leave the site.
    """
    make_entry("e1", "A record")

    reader = csv.reader(io.StringIO(client.get(URL).content.decode()))

    assert next(reader) == [
        "Description",
        "Summary",
        "Year",
        "Jurisdiction",
        "Region",
        "Topic",
        "Type",
        "Type of resource",
        "Link",
        "Record URL",
    ]


def test_a_record_fills_every_column():
    region = Region.objects.create(name="Africa")
    kenya = CountryTag.objects.create(notion_id="c-ke", name="Kenya", slug="kenya")
    kenya.regions.add(region)

    entry = make_entry("e1", "A Kenyan case", topics=["Tax"])
    entry.countries.add(kenya)
    entry.data_users.add(DataUserTag.objects.get_or_create(name="Journalist")[0])
    entry.resource_types.add(ResourceTypeTag.objects.get_or_create(name="Media article")[0])

    row = rows(client.get(URL))[0]

    assert row["Description"] == "A Kenyan case"
    assert row["Summary"] == "Summary of A Kenyan case"
    assert row["Year"] == "2024"
    assert row["Jurisdiction"] == "Kenya"
    assert row["Region"] == "Africa"
    assert row["Topic"] == "Tax"
    assert row["Type"] == "Journalist"
    assert row["Type of resource"] == "Media article"
    assert row["Link"] == "https://example.com/source"
    root_url = Site.objects.get(is_default_site=True).root_url
    assert row["Record URL"] == f"{root_url}{entry.get_absolute_url()}"


def test_several_values_in_one_column_are_separated():
    """Semicolons rather than commas, so a value holding a comma stays readable."""
    entry = make_entry("e1", "A record", topics=["Tax", "Corruption"])
    entry.countries.add(CountryTag.objects.create(notion_id="c-ke", name="Kenya", slug="kenya"))
    entry.countries.add(
        CountryTag.objects.create(notion_id="c-uk", name="United Kingdom", slug="uk"),
    )

    row = rows(client.get(URL))[0]

    assert sorted(row["Topic"].split("; ")) == ["Corruption", "Tax"]
    assert sorted(row["Jurisdiction"].split("; ")) == ["Kenya", "United Kingdom"]


def test_a_record_with_no_year_exports_a_blank():
    make_entry("e1", "A record", year=None)

    assert rows(client.get(URL))[0]["Year"] == ""


def test_a_record_with_no_jurisdiction_but_international_says_so():
    entry = make_entry("e1", "A worldwide record")
    entry.international = True
    entry.save()

    assert rows(client.get(URL))[0]["Jurisdiction"] == "International"


####################################################################################################
# The link on the listing
####################################################################################################


def test_the_listing_offers_the_export(bot_centre, indexed):  # noqa: ARG001
    make_entry("e1", "A record")

    assert URL in client.get(bot_centre.url).rendered_content


def test_a_degraded_listing_does_not_offer_the_export(bot_centre):
    """With search down there are no filters to carry, so the file would
    quietly be the whole dataset whatever the reader had asked for.
    """
    rendered = client.get(f"{bot_centre.url}?topic=Tax").rendered_content

    assert URL not in rendered


def test_the_listing_carries_the_current_query_into_the_export(bot_centre, indexed):  # noqa: ARG001
    make_entry("e1", "A tax case", topics=["Tax"])

    rendered = client.get(f"{bot_centre.url}?topic=Tax").rendered_content

    assert f"{URL}?topic=Tax" in rendered


def test_the_record_url_is_absolute_and_keeps_the_site_scheme():
    """SECURE_PROXY_SSL_HEADER is not configured, so Django sees plain http
    behind the TLS proxy. Wagtail's site record carries the real scheme, and a
    CSV Open Ownership may hand out must not be full of http:// links.
    """
    make_entry("e1", "A record")

    url = rows(client.get(URL))[0]["Record URL"]

    assert url.startswith(Site.objects.get(is_default_site=True).root_url)
    assert "://" in url

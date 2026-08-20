import pytest
from django.test import Client
from django.urls import reverse

from modules.content.models.pages import BotCentrePage
from modules.notion.models import DataUserTag, ImpactEntry, PolicyAreaTag, ResourceTypeTag

pytestmark = pytest.mark.django_db

client = Client()

# A real Notion id, which is a dashed UUID. Records have no title field, so the
# Notion id is what the detail URL is keyed on.
NOTION_ID = "78612aa2-0e23-447e-b790-8086c8488b8d"


####################################################################################################
# Helpers
####################################################################################################


@pytest.fixture(autouse=True)
def bot_centre(home_page):
    """The listing page, which every test needs whether it names it or not: the
    detail view looks it up for the breadcrumb and the close link.
    """
    page = BotCentrePage(title="Evidence Centre")
    home_page.add_child(instance=page)
    page.save_revision().publish()
    return page


def make_entry(notion_id=NOTION_ID, description="A useful record", publish=True, link=None):
    return ImpactEntry.objects.create(
        notion_id=notion_id,
        description=description,
        summary=f"Summary of {description}",
        year=2024,
        publish=publish,
        source_url="https://example.com/source" if link is None else link,
    )


def detail_url(entry):
    return reverse("evidence-detail", kwargs={"notion_id": entry.notion_id})


####################################################################################################
# Which records have a page
####################################################################################################


def test_a_publishable_record_has_a_page():
    entry = make_entry()

    response = client.get(detail_url(entry))

    assert response.status_code == 200
    assert entry.description in response.content.decode()


def test_an_uncleared_record_has_no_page():
    """`publish` is Open Ownership's clearance flag. Without it the record is
    synced but must not be reachable.
    """
    entry = make_entry(publish=False)

    assert client.get(detail_url(entry)).status_code == 404


def test_a_record_with_no_link_has_no_page():
    """Open Ownership asked for linkless records to be left out of the listing,
    so they must not be reachable by URL either.
    """
    entry = make_entry(link="")

    assert client.get(detail_url(entry)).status_code == 404


def test_a_deleted_record_has_no_page():
    entry = make_entry()
    entry.deleted = True
    entry.save()

    assert client.get(detail_url(entry)).status_code == 404


def test_an_unknown_notion_id_is_a_404():
    url = reverse("evidence-detail", kwargs={"notion_id": "11111111-2222-3333-4444-555555555555"})

    assert client.get(url).status_code == 404


####################################################################################################
# Full page versus fragment
####################################################################################################


def test_a_normal_request_gets_a_whole_page():
    entry = make_entry()

    body = client.get(detail_url(entry)).content.decode()

    assert "<html" in body
    assert "</body>" in body


def test_an_htmx_request_gets_only_the_card():
    """The same view answers both. htmx sends `HX-Request` on every request it
    makes, so no separate URL is needed for the fragment.
    """
    entry = make_entry()

    response = client.get(detail_url(entry), headers={"HX-Request": "true"})
    body = response.content.decode()

    assert response.status_code == 200
    assert "<html" not in body
    assert entry.description in body


def test_an_htmx_request_can_ask_for_the_collapsed_card():
    """What the close control fetches, so a reader can shut a record again
    without a page load.
    """
    entry = make_entry()
    entry.resource_types.add(ResourceTypeTag.objects.get_or_create(name="Media article")[0])

    body = client.get(
        f"{detail_url(entry)}?collapsed=1",
        headers={"HX-Request": "true"},
    ).content.decode()

    assert entry.description in body
    assert "Media article" not in body


def test_the_expanded_card_shows_detail_the_collapsed_card_hides():
    """Open Ownership asked for description, jurisdiction, topic and year while
    a record is shut, and everything public once it is open.
    """
    entry = make_entry()
    entry.resource_types.add(ResourceTypeTag.objects.get_or_create(name="Media article")[0])
    entry.data_users.add(DataUserTag.objects.get_or_create(name="Journalist")[0])

    body = client.get(detail_url(entry), headers={"HX-Request": "true"}).content.decode()

    assert "Media article" in body
    assert "Journalist" in body


def test_an_opened_record_offers_the_source():
    """Which is where the link went when it came off the shut card."""
    entry = make_entry()

    body = client.get(detail_url(entry), headers={"HX-Request": "true"}).content.decode()

    assert "View source" in body
    assert entry.source_url in body


def test_a_worldwide_record_names_its_jurisdiction_as_global():
    entry = make_entry()
    entry.worldwide = True
    entry.save()

    body = client.get(detail_url(entry)).content.decode()

    assert "<dd>Global</dd>" in body


def test_the_records_values_link_back_to_a_filtered_listing(bot_centre):  # noqa: ARG001
    """Every value on the page that is a filter can be clicked to see the other
    records sharing it.
    """
    entry = make_entry()
    entry.resource_types.add(ResourceTypeTag.objects.get_or_create(name="Media article")[0])

    body = client.get(detail_url(entry)).content.decode()

    assert "?year=2024" in body
    assert "?resource=Media+article" in body


def test_the_data_user_is_not_a_link(bot_centre):  # noqa: ARG001
    """"Type" was taken out of the filters, so there is nothing to click through
    to.
    """
    entry = make_entry()
    entry.data_users.add(DataUserTag.objects.get_or_create(name="Journalist")[0])

    body = client.get(detail_url(entry)).content.decode()

    assert "?type=" not in body


####################################################################################################
# The listing links to it
####################################################################################################


def test_the_listing_card_links_to_the_detail_url(bot_centre):
    """The expand control is a plain link first, so the listing still works with
    JavaScript off.
    """
    entry = make_entry()
    entry.policy_areas.add(PolicyAreaTag.objects.get_or_create(name="Tax")[0])

    body = client.get(bot_centre.url).content.decode()

    assert f'href="{detail_url(entry)}"' in body

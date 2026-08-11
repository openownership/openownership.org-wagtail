import pytest
from django.test import Client

from modules.content.models.pages import BotCentrePage
from modules.notion.models import CountryTag, ImpactEntry, PolicyAreaTag, ResourceTypeTag

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


def make_entry(notion_id, description, year=2024, publish=True, policy_areas=(), link=None):
    entry = ImpactEntry.objects.create(
        notion_id=notion_id,
        description=description,
        summary=f"Summary of {description}",
        year=year,
        publish=publish,
        source_url="https://example.com/source" if link is None else link,
    )
    for name in policy_areas:
        entry.policy_areas.add(PolicyAreaTag.objects.get_or_create(name=name)[0])
    return entry


####################################################################################################
# The page itself
####################################################################################################


def test_bot_centre_page_200s(bot_centre):
    assert client.get(bot_centre.url).status_code == 200


def test_entries_are_listed(bot_centre):
    make_entry("e1", "Kenyan FIU used BO data in an investigation")

    rendered = client.get(bot_centre.url).rendered_content

    assert "Kenyan FIU used BO data in an investigation" in rendered


def test_the_summary_is_shown(bot_centre):
    make_entry("e1", "Kenyan FIU used BO data")

    rendered = client.get(bot_centre.url).rendered_content

    assert "Summary of Kenyan FIU used BO data" in rendered


def test_entries_not_cleared_for_publication_are_hidden(bot_centre):
    make_entry("e1", "Cleared for publication")
    make_entry("e2", "Still internal", publish=False)

    rendered = client.get(bot_centre.url).rendered_content

    assert "Cleared for publication" in rendered
    assert "Still internal" not in rendered


def test_entries_with_no_link_are_hidden(bot_centre):
    """OO asked for records with nothing to link to be left out entirely."""
    make_entry("e1", "Has a source")
    make_entry("e2", "Nothing to link to", link="")

    rendered = client.get(bot_centre.url).rendered_content

    assert "Has a source" in rendered
    assert "Nothing to link to" not in rendered


def test_a_long_summary_is_cut_short_on_the_card(bot_centre):
    entry = make_entry("e1", "An entry")
    entry.summary = " ".join(f"word{n}" for n in range(120))
    entry.save()

    rendered = client.get(bot_centre.url).rendered_content

    assert "word10" in rendered
    assert "word119" not in rendered


def test_soft_deleted_entries_are_hidden(bot_centre):
    entry = make_entry("e1", "Gone from Notion")
    entry.deleted = True
    entry.save()

    assert "Gone from Notion" not in client.get(bot_centre.url).rendered_content


def test_the_card_shows_description_jurisdiction_topic_and_year(bot_centre):
    """The four fields OO asked for on a collapsed record."""
    entry = make_entry("e1", "An entry about something", year=2019, policy_areas=["Tax"])
    entry.countries.add(CountryTag.objects.create(notion_id="c1", name="Kenya", slug="kenya"))

    rendered = client.get(bot_centre.url).rendered_content

    assert "An entry about something" in rendered
    assert "Kenya" in rendered
    assert "Tax" in rendered
    assert "2019" in rendered


def test_the_card_holds_back_the_rest_until_expansion(bot_centre):
    entry = make_entry("e1", "An entry", year=2019)
    entry.resource_types.add(ResourceTypeTag.objects.create(name="Public sector"))

    assert "Public sector" not in client.get(bot_centre.url).rendered_content


####################################################################################################
# Ordering
####################################################################################################


def test_newest_year_comes_first(bot_centre):
    make_entry("old", "An older entry", year=2019)
    make_entry("new", "A newer entry", year=2026)

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["new", "old"]


def test_within_a_year_entries_are_ordered_by_topic(bot_centre):
    make_entry("tax", "Second by topic", year=2024, policy_areas=["Tax"])
    make_entry("aml", "First by topic", year=2024, policy_areas=["AML/CFT"])

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["aml", "tax"]


def test_entries_without_a_topic_come_last(bot_centre):
    make_entry("none", "No topic at all", year=2024)
    make_entry("tax", "Has a topic", year=2024, policy_areas=["Tax"])

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["tax", "none"]


def test_entries_without_a_year_come_last(bot_centre):
    make_entry("dated", "Has a year", year=2019)
    make_entry("undated", "No year", year=None)

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["dated", "undated"]


def test_the_same_year_and_topic_falls_back_to_alphabetical(bot_centre):
    make_entry("b", "Beta comes second", year=2024, policy_areas=["Tax"])
    make_entry("a", "Alpha comes first", year=2024, policy_areas=["Tax"])

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["a", "b"]


def test_an_entry_with_several_topics_is_not_repeated(bot_centre):
    make_entry("e1", "Several topics", year=2024, policy_areas=["Tax", "Corruption"])

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["e1"]


####################################################################################################
# Pagination
####################################################################################################


def test_the_first_page_holds_one_page_worth(bot_centre):
    for index in range(BotCentrePage.objects_per_page + 5):
        make_entry(f"e{index}", f"Entry {index:03d}", year=2024)

    page_obj = client.get(bot_centre.url).context_data["page_obj"]

    assert len(page_obj.object_list) == BotCentrePage.objects_per_page
    assert page_obj.paginator.count == BotCentrePage.objects_per_page + 5


def test_the_second_page_holds_the_rest(bot_centre):
    for index in range(BotCentrePage.objects_per_page + 5):
        make_entry(f"e{index}", f"Entry {index:03d}", year=2024)

    page_obj = client.get(f"{bot_centre.url}?page=2").context_data["page_obj"]

    assert len(page_obj.object_list) == 5
    assert page_obj.number == 2


def test_pagination_links_appear_when_there_is_more_than_one_page(bot_centre):
    for index in range(BotCentrePage.objects_per_page + 1):
        make_entry(f"e{index}", f"Entry {index:03d}", year=2024)

    rendered = client.get(bot_centre.url).rendered_content

    assert "?page=2" in rendered


def test_no_pagination_when_everything_fits(bot_centre):
    make_entry("e1", "The only entry")

    assert "?page=2" not in client.get(bot_centre.url).rendered_content


def test_an_out_of_range_page_falls_back_to_the_last_one(bot_centre):
    make_entry("e1", "The only entry")

    page_obj = client.get(f"{bot_centre.url}?page=99").context_data["page_obj"]

    assert page_obj.number == 1


def test_a_nonsense_page_number_falls_back_to_the_first(bot_centre):
    make_entry("e1", "The only entry")

    page_obj = client.get(f"{bot_centre.url}?page=banana").context_data["page_obj"]

    assert page_obj.number == 1


####################################################################################################
# Empty state
####################################################################################################


def test_the_page_still_renders_with_no_entries(bot_centre):
    response = client.get(bot_centre.url)

    assert response.status_code == 200
    assert response.context_data["page_obj"].paginator.count == 0

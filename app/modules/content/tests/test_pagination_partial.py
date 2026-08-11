"""Tests for the shared pagination partial and the query-string helper it uses.

The partial is included by nine templates, so its behaviour is pinned here
rather than only through whichever page happens to exercise it.
"""

# 3rd party
import pytest
from django.test import Client, RequestFactory

# Project
from config.template import pagination_query

# Module
from modules.content.models.pages import BotCentrePage
from modules.notion.models import ImpactEntry, PolicyAreaTag

pytestmark = pytest.mark.django_db

client = Client()


####################################################################################################
# The helper
####################################################################################################


def request_for(querystring):
    return RequestFactory().get(f"/?{querystring}")


def test_the_page_number_is_dropped():
    assert "page" not in pagination_query(request_for("topic=Tax&page=3"))


def test_every_other_parameter_is_kept():
    params = pagination_query(request_for("q=tax&topic=Tax&sort=az&page=3"))

    assert "q=tax" in params
    assert "topic=Tax" in params
    assert "sort=az" in params


def test_repeated_parameters_are_all_kept():
    """Multi-select filters send the same key more than once."""
    params = pagination_query(request_for("topic=Tax&topic=Corruption"))

    assert params.count("topic=") == 2


def test_no_parameters_gives_an_empty_string():
    assert pagination_query(request_for("")) == ""


def test_no_request_gives_an_empty_string():
    assert pagination_query(None) == ""


####################################################################################################
# The partial, rendered
####################################################################################################


@pytest.fixture
def paginated(home_page):
    page = BotCentrePage(title="Evidence Centre")
    home_page.add_child(instance=page)
    page.save_revision().publish()

    tax = PolicyAreaTag.objects.create(name="Tax")
    for index in range(30):
        entry = ImpactEntry.objects.create(
            notion_id=f"e{index}",
            description=f"Entry {index:03d}",
            source_url=f"https://example.com/{index}",
            year=2024,
            publish=True,
        )
        entry.policy_areas.add(tax)
    return page


def test_page_links_appear(paginated):
    assert "page=2" in client.get(paginated.url).rendered_content


def test_a_filter_survives_the_click_to_page_two(paginated):
    rendered = client.get(f"{paginated.url}?topic=Tax").rendered_content

    assert "topic=Tax&amp;page=2" in rendered


def test_a_sort_survives_the_click_to_page_two(paginated):
    rendered = client.get(f"{paginated.url}?sort=az").rendered_content

    assert "sort=az&amp;page=2" in rendered


def test_a_keyword_survives_the_click_to_page_two(paginated):
    rendered = client.get(f"{paginated.url}?q=Entry").rendered_content

    assert "q=Entry&amp;page=2" in rendered


def test_the_current_page_link_keeps_the_query_string(paginated):
    """It used to be href="./", which silently reset every filter."""
    rendered = client.get(f"{paginated.url}?topic=Tax").rendered_content

    assert 'href="./"' not in rendered
    assert 'aria-current="page"' in rendered


def test_the_elided_range_follows_the_reader(paginated):
    """It used to always elide around page 1, so there was no way forward."""
    rendered = client.get(f"{paginated.url}?page=3").rendered_content

    assert "page=3" in rendered
    assert "page=2" in rendered


def test_no_pagination_when_it_all_fits(home_page):
    page = BotCentrePage(title="Small")
    home_page.add_child(instance=page)
    page.save_revision().publish()
    ImpactEntry.objects.create(
        notion_id="only",
        description="The only entry",
        source_url="https://example.com/only",
        publish=True,
    )

    assert "page=2" not in client.get(page.url).rendered_content

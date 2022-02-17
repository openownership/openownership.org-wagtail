import pytest

from django.test import Client

from modules.content.models import ArticlePage, TeamProfilePage

pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_siblings(team_page):
    "Should include all the page's siblings"

    parent = team_page.get_parent()

    article_1 = ArticlePage(live=True, title="Article 1")
    parent.add_child(instance=article_1)

    article_2 = ArticlePage(live=True, title="Article 2")
    parent.add_child(instance=article_2)

    # Shouldn't be included:
    draft_article = ArticlePage(live=False, title="Draft article")
    parent.add_child(instance=draft_article)

    rv = client.get(team_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu) == 3
    assert menu[0]["page"].specific == team_page
    assert menu[1]["page"].specific == article_1
    assert menu[2]["page"].specific == article_2


def test_menu_pages_children(team_page):
    "Should include any child pages"

    profile_1 = TeamProfilePage(live=True, title="Profile 1")
    team_page.add_child(instance=profile_1)

    profile_2 = TeamProfilePage(live=True, title="Profile 2")
    team_page.add_child(instance=profile_2)

    # Shouldn't be included:
    draft_profile = TeamProfilePage(live=False, title="Draft profile")
    team_page.add_child(instance=draft_profile)

    rv = client.get(team_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu[0]["children"]) == 2
    assert menu[0]["children"][0].specific == profile_1
    assert menu[0]["children"][1].specific == profile_2

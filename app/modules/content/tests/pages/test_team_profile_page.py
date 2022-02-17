import pytest

from django.test import Client

from modules.content.models import ArticlePage, TeamProfilePage

pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_elders(team_profile_page):
    "Should include parents' siblings"

    grand_parent = team_profile_page.get_parent().get_parent()

    article_1 = ArticlePage(live=True, title="Article 1")
    grand_parent.add_child(instance=article_1)

    article_2 = ArticlePage(live=True, title="Article 2")
    grand_parent.add_child(instance=article_2)

    # Shouldn't be included:
    draft_article = ArticlePage(live=False, title="Draft article")
    grand_parent.add_child(instance=draft_article)

    rv = client.get(team_profile_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu) == 3
    assert menu[0]["page"].specific == team_profile_page.get_parent()
    assert menu[1]["page"].specific == article_1
    assert menu[2]["page"].specific == article_2


def test_menu_pages_siblings(team_profile_page):
    "Should include any sibling team profile pages"

    parent = team_profile_page.get_parent()

    profile_2 = TeamProfilePage(live=True, title="Profile 2")
    parent.add_child(instance=profile_2)

    profile_3 = TeamProfilePage(live=True, title="Profile 3")
    parent.add_child(instance=profile_3)

    # Shouldn't be included:
    draft_profile = TeamProfilePage(live=False, title="Draft profile")
    parent.add_child(instance=draft_profile)

    rv = client.get(team_profile_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu[0]["children"]) == 3
    assert menu[0]["children"][0].specific == team_profile_page
    assert menu[0]["children"][1].specific == profile_2
    assert menu[0]["children"][2].specific == profile_3

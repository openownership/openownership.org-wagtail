import pytest

from django.test import Client

from modules.content.models import ArticlePage, SectionListingPage


pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_live(article_page):
    "Should only include live sibling pages, not draft ones"

    section_page = article_page.get_parent()

    live_sibling = ArticlePage(live=True, title="Live")
    section_page.add_child(instance=live_sibling)

    draft_sibling = ArticlePage(live=False, title="Draft")
    section_page.add_child(instance=draft_sibling)

    rv = client.get(article_page.url)

    pages = [p.specific for p in rv.context_data["menu_pages"]]
    assert article_page in pages
    assert live_sibling in pages
    assert draft_sibling not in pages


def test_menu_pages_only_siblings(article_page):
    "Should only include sibling pages, not other ArticlePages"

    home_page = article_page.get_parent().get_parent()

    # A new section:
    section_2 = SectionListingPage(title="Section 2")
    home_page.add_child(instance=section_2)

    # With a child article:
    non_sibling = ArticlePage(live=True, title="Non Sibling")
    section_2.add_child(instance=non_sibling)

    rv = client.get(article_page.url)

    pages = [p.specific for p in rv.context_data["menu_pages"]]
    assert non_sibling not in pages

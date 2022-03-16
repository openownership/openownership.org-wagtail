import pytest

from django.test import Client

from modules.content.models import ArticlePage


pytestmark = pytest.mark.django_db

client = Client()


def test_show_child_pages_true(section_listing_page):
    "Live child pages should be visible"
    p1 = ArticlePage(live=True, title="Article 1")
    section_listing_page.add_child(instance=p1)
    p1.save()

    p2 = ArticlePage(live=True, title="Article 2")
    section_listing_page.add_child(instance=p2)
    p2.save()

    # Shouldn't be visible:
    p3 = ArticlePage(live=False, title="Article 3")
    section_listing_page.add_child(instance=p3)
    p3.save()

    rv = client.get(section_listing_page.url)

    pages = [p.specific for p in rv.context_data["child_pages"]]
    assert p1 in pages
    assert p2 in pages
    assert p3 not in pages


def test_show_child_pages_false(section_listing_page):
    "Not even live child pages should be visible if show_child_pages is False"
    section_listing_page.show_child_pages = False
    section_listing_page.save_revision().publish()

    p1 = ArticlePage(live=True, title="Article 1")
    section_listing_page.add_child(instance=p1)
    p1.save()

    rv = client.get(section_listing_page.url)

    pages = [p.specific for p in rv.context_data["child_pages"]]
    assert p1 not in pages


def test_card_blurb(section_listing_page):
    section_listing_page.blurb = "My blurb"
    assert section_listing_page.card_blurb == "My blurb"

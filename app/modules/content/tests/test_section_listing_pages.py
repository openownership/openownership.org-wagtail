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

    assert p1.title in rv.rendered_content
    assert p2.title in rv.rendered_content
    assert p3.title not in rv.rendered_content


def test_show_child_pages_false(section_listing_page):
    "No child pages should be visible"
    section_listing_page.show_child_pages = False
    section_listing_page.save_revision().publish()

    p1 = ArticlePage(live=True, title="Article 1")
    section_listing_page.add_child(instance=p1)
    p1.save()

    p2 = ArticlePage(live=False, title="Article 2")
    section_listing_page.add_child(instance=p2)
    p2.save()

    rv = client.get(section_listing_page.url)

    assert p1.title not in rv.rendered_content
    assert p2.title not in rv.rendered_content

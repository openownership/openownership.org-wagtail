import arrow
import pytest

from modules.content.models import Author, PressLinkAuthorRelationship


pytestmark = pytest.mark.django_db


def test_authors(author, press_link):
    "The authors property should work as expected"

    author_2 = Author.objects.create(name="Terry Collier")

    PressLinkAuthorRelationship(snippet=press_link, author=author).save()
    PressLinkAuthorRelationship(snippet=press_link, author=author_2).save()

    authors = press_link.authors
    assert len(authors) == 2
    assert author in authors
    assert author_2 in authors


def test_is_press_link(press_link):
    assert press_link.is_press_link is True


def test_get_url(press_link):
    assert press_link.get_url() == press_link.url


def test_specific(press_link):
    assert press_link.specific == press_link


def test_display_date(press_link):
    assert press_link.display_date == press_link.first_published_at


def test_human_display_date(press_link):
    dt = arrow.get("2022-01-09 12:00:00").datetime
    press_link.first_published_at = dt
    assert press_link.human_display_date == "09 January 2022"

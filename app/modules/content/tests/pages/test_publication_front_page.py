import arrow
import pytest

from django.core.management import call_command
from django.test import Client

from modules.content.models import (
    Author,
    PublicationAuthorRelationship,
    PublicationFrontPage,
    PublicationInnerPage,
)
from modules.taxonomy.models import PublicationType


pytestmark = pytest.mark.django_db

client = Client()


def test_date(publication_front_page):
    "date should be the same as display_date"
    p = publication_front_page
    dt = arrow.get("2022-01-31 12:00:00").datetime
    p.display_date = dt
    assert p.date == dt


def test_human_display_date(publication_front_page):
    "human_display_date should return the correct string"
    p = publication_front_page
    dt = arrow.get("2022-01-31 12:00:00").datetime
    p.display_date = dt
    assert p.human_display_date == "31 January 2022"


def test_display_title(publication_front_page):
    "display_title should return the page.title"
    p = publication_front_page
    p.title = "My special title"
    assert p.display_title == "My special title"


def test_authors(author, publication_front_page):
    "authors should return the authors"
    p = publication_front_page

    author_2 = Author.objects.create(name="Terry Collier")

    PublicationAuthorRelationship(page=p, author=author).save()
    PublicationAuthorRelationship(page=p, author=author_2).save()

    authors = p.authors
    assert len(authors) == 2
    assert author in authors
    assert author_2 in authors


def test_menu_pages_self(publication_front_page):
    "Should include itself with the correct title in menu_pages"
    p = publication_front_page

    p.page_title = "Introduction"
    p.save_revision().publish()

    rv = client.get(p.url)

    menu = rv.context_data['menu_pages']
    assert len(menu) == 1
    assert menu[0].specific == p
    assert menu[0].title == 'Introduction'


def test_menu_pages_children(publication_front_page):
    "Should include live children in menu_pages"
    parent = publication_front_page

    p1 = PublicationInnerPage(live=True, title="Inner 1")
    parent.add_child(instance=p1)
    p1.save_revision().publish()

    p2 = PublicationInnerPage(live=True, title="Inner 2")
    parent.add_child(instance=p2)
    p2.save_revision().publish()

    # Shouldn't be included:
    p3 = PublicationInnerPage(live=False, title="Inner 3")
    parent.add_child(instance=p3)
    p3.save_revision()

    rv = client.get(parent.url)

    menu = rv.context_data['menu_pages']
    assert len(menu) == 3
    assert menu[0].specific == parent
    assert menu[1].specific == p1
    assert menu[2].specific == p2


def test_publication_type_choices(publication_front_page):
    """It should return the only PublicationTypes availeble to this page,
    but this page now allows all publication types."""
    call_command('populate_taxonomies', verbosity=0)
    types = publication_front_page.get_publication_type_choices()

    assert len(types) == 8
    assert isinstance(types[0], PublicationType)


def test_get_next_page(publication_front_page):
    "get_next_page() should return the first live inner page"
    parent = publication_front_page

    last_child = PublicationInnerPage(live=True, title="Last")
    parent.add_child(instance=last_child)

    # Add before the last child:
    first_child = PublicationInnerPage(live=True, title="First")
    last_child.add_sibling(pos="left", instance=first_child)

    # Add very first; but it's not live, so shouldn't be included:
    draft_child = PublicationInnerPage(live=False, title="Draft")
    first_child.add_sibling(pos="left", instance=draft_child)

    assert publication_front_page.get_next_page().specific == first_child


def test_get_next_page_none(publication_front_page):
    "get_next_page() should return None if there are no live inner pages"
    parent = publication_front_page

    draft_child = PublicationInnerPage(live=False, title="Draft")
    parent.add_child(instance=draft_child)

    assert publication_front_page.get_next_page() is None


def test_breadcrumb_page(publication_front_page):
    "It should return the parent Section page"
    assert publication_front_page.breadcrumb_page == publication_front_page.get_parent()


def test_card_blurb(publication_front_page):
    publication_front_page.blurb = "My blurb"
    assert publication_front_page.card_blurb == "My blurb"


def test_show_display_date_on_card(publication_front_page):
    "It should match the show_display_date property"
    p = publication_front_page

    p.show_display_date = True
    assert p.show_display_date_on_card is True

    p.show_display_date = False
    assert p.show_display_date_on_card is False


def test_show_display_date_on_page(publication_front_page):
    "It should match the show_display_date property"
    p = publication_front_page

    p.show_display_date = True
    assert p.show_display_date_on_page is True

    p.show_display_date = False
    assert p.show_display_date_on_page is False

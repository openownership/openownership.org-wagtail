import arrow
import pytest

from django.test import Client

from modules.content.models import PublicationAuthorRelationship, PublicationInnerPage


pytestmark = pytest.mark.django_db

client = Client()


def test_display_title(publication_inner_page):
    "display_title should return the parent's page.title"
    p = publication_inner_page
    p.get_parent().title = "My special title"
    assert p.display_title == "My special title"


def test_authors(author, publication_inner_page):
    "authors should return the parent's authors"
    p = publication_inner_page
    parent = p.get_parent()

    PublicationAuthorRelationship(page=parent, author=author).save()

    assert p.authors[0] == author


def test_date(publication_inner_page):
    "date should be the same as parent's display_date"
    p = publication_inner_page
    dt = arrow.get("2022-01-31 12:00:00").datetime
    p.get_parent().display_date = dt
    assert p.date == dt


def test_human_display_date(publication_inner_page):
    "human_display_date should return the correct string, from parent's date"
    p = publication_inner_page
    dt = arrow.get("2022-01-31 12:00:00").datetime
    p.get_parent().display_date = dt
    assert p.human_display_date == "31 January 2022"


def test_menu_pages_parent(publication_inner_page):
    "Should include parent with the correct title in menu_pages"
    p = publication_inner_page
    parent = p.get_parent()

    parent.page_title = "Introduction"
    parent.save_revision().publish()

    rv = client.get(p.url)

    pages = rv.context_data['menu_pages']
    assert pages[0].specific == parent
    assert pages[0].title == 'Introduction'


def test_menu_pages_children(publication_inner_page):
    "Should include live siblings in menu_pages"
    p1 = publication_inner_page
    parent = p1.get_parent()

    p2 = PublicationInnerPage(live=True, title="Inner 2")
    parent.add_child(instance=p2)
    p2.save_revision().publish()

    # Shouldn't be included:
    p3 = PublicationInnerPage(live=False, title="Inner 3")
    parent.add_child(instance=p3)
    p3.save_revision()

    rv = client.get(parent.url)

    pages = rv.context_data['menu_pages']
    assert len(pages) == 3
    assert pages[0].specific == parent
    assert pages[1].specific == p1
    assert pages[2].specific == p2

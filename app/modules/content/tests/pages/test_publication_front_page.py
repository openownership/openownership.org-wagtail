import arrow
import pytest

from django.test import Client

from modules.content.models import Author, PublicationAuthorRelationship, PublicationInnerPage


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

    pages = rv.context_data['menu_pages']
    assert pages[0].specific == p
    assert pages[0].title == 'Introduction'


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

    pages = rv.context_data['menu_pages']
    assert len(pages) == 3
    assert pages[0].specific == parent
    assert pages[1].specific == p1
    assert pages[2].specific == p2

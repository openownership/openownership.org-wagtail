import arrow
import pytest

from django.core.management import call_command

from modules.content.models import BlogArticlePage
from modules.taxonomy.models import PublicationType


def test_human_display_date(blog_article_page):
    "It should return the display date in correct format"
    dt = arrow.get("2022-01-09 12:00:00").datetime
    blog_article_page.display_date = dt
    assert blog_article_page.human_display_date == "09 January 2022"


def test_publication_type_choices(blog_article_page):
    "It should return the only PublicationTypes availeble to this page"
    call_command('populate_taxonomies', verbosity=0)

    types = blog_article_page.get_publication_type_choices()

    assert len(types) == 1
    assert isinstance(types[0], PublicationType)
    assert types[0].name == "Blog post"


def test_breadcrumb_page(blog_article_page):
    "It should return the parent Blog page"
    assert blog_article_page.breadcrumb_page == blog_article_page.get_parent()

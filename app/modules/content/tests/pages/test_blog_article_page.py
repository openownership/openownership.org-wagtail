import arrow
import pytest

from django.core.management import call_command
from django.test import Client

from modules.content.models import BlogArticlePage
from modules.taxonomy.models import PublicationType


client = Client()


def test_human_display_date(blog_article_page):
    "It should return the display date in correct format"
    dt = arrow.get("2022-01-09 12:00:00").datetime
    blog_article_page.display_date = dt
    assert blog_article_page.human_display_date == "09 January 2022"


def test_publication_type_choices(blog_article_page):
    """It should return the only PublicationTypes availeble to this page,
    but this page now allows all publication types."""
    call_command('populate_taxonomies', verbosity=0)

    types = blog_article_page.get_publication_type_choices()

    assert len(types) == 8
    assert isinstance(types[0], PublicationType)
    # Blog post is no longer a publication type
    assert types[0].name != "Blog post"


def test_breadcrumb_page(blog_article_page):
    "It should return the parent Blog page"
    assert blog_article_page.breadcrumb_page == blog_article_page.get_parent()


def test_card_blurb(blog_article_page):
    blog_article_page.blurb = "My blurb"
    assert blog_article_page.card_blurb == "My blurb"


def test_show_sharing_buttons(blog_article_page):
    "With no show_sharing_buttons setting, the page should still show sharing buttons"
    res = client.get(blog_article_page.url)
    assert '<div class="share-page">' in res.rendered_content

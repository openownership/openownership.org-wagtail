import arrow
import pytest

from django.core.management import call_command

from modules.content.models import NewsArticlePage
from modules.taxonomy.models import PublicationType


def test_human_display_date(news_article_page):
    "It should return the display date in correct format"
    dt = arrow.get("2022-01-09 12:00:00").datetime
    news_article_page.display_date = dt
    assert news_article_page.human_display_date == "09 January 2022"


def test_publication_type_choices(news_article_page):
    """It should return the only PublicationTypes availeble to this page,
    but this page now allows all publication types."""
    call_command('populate_taxonomies', verbosity=0)

    types = news_article_page.get_publication_type_choices()

    assert len(types) == 8
    assert isinstance(types[0], PublicationType)
    # News article is no longer a publication type
    assert types[0].name != "News article"


def test_breadcrumb_page(news_article_page):
    "It should return the parent News page"
    assert news_article_page.breadcrumb_page == news_article_page.get_parent()


def test_card_blurb(news_article_page):
    news_article_page.blurb = "My blurb"
    assert news_article_page.card_blurb == "My blurb"

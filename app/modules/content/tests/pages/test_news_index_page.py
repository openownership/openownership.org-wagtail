import pytest

from django.test import Client

from modules.content.models import ArticlePage, BlogIndexPage

pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_siblings(news_index_page):
    "Should include all the page's siblings"

    parent = news_index_page.get_parent()

    blog_index_page = BlogIndexPage(live=True, title="Blog")
    parent.add_child(instance=blog_index_page)

    article = ArticlePage(live=True, title="Article")
    parent.add_child(instance=article)

    # Shouldn't be included:
    draft_article = ArticlePage(live=False, title="Draft article")
    parent.add_child(instance=draft_article)

    rv = client.get(news_index_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu) == 3
    assert menu[0]["page"].specific == news_index_page
    assert menu[1]["page"].specific == blog_index_page
    assert menu[2]["page"].specific == article
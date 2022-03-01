import pytest

from django.test import Client

from modules.content.models import ArticlePage, BlogArticlePage, NewsIndexPage

pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_siblings(blog_index_page):
    "Should include all the page's siblings"

    parent = blog_index_page.get_parent()

    news_index_page = NewsIndexPage(live=True, title="News")
    parent.add_child(instance=news_index_page)

    article = ArticlePage(live=True, title="Article")
    parent.add_child(instance=article)

    # Shouldn't be included:
    draft_article = ArticlePage(live=False, title="Draft article")
    parent.add_child(instance=draft_article)

    rv = client.get(blog_index_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu) == 3
    assert menu[0]["page"].specific == blog_index_page
    assert menu[1]["page"].specific == news_index_page
    assert menu[2]["page"].specific == article


def test_menu_pages_no_children(blog_index_page):
    "Should not include child pages if we're on the index page"

    article = BlogArticlePage(live=True, title="Article")
    blog_index_page.add_child(instance=article)
    article.save_revision().publish()

    rv = client.get(blog_index_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu) == 1
    assert menu[0]["page"].specific == blog_index_page
    assert len(menu[0]["children"]) == 0

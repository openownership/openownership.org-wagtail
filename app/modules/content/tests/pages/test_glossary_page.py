import pytest

from django.test import Client

from modules.content.models import ArticlePage

pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_siblings(glossary_page):
    "Should include all the page's siblings"

    parent = glossary_page.get_parent()

    article_1 = ArticlePage(live=True, title="Article 1")
    parent.add_child(instance=article_1)

    article_2 = ArticlePage(live=True, title="Article 2")
    parent.add_child(instance=article_2)

    # Shouldn't be included:
    draft_article = ArticlePage(live=False, title="Draft article")
    parent.add_child(instance=draft_article)

    rv = client.get(glossary_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu) == 3
    assert menu[0]["page"].specific == glossary_page
    assert menu[1]["page"].specific == article_1
    assert menu[2]["page"].specific == article_2

import pytest

from django.test import Client

from modules.content.models import ArticlePage, NewsIndexPage, SectionPage
from modules.taxonomy.views import SectionLatestPagesView


pytestmark = pytest.mark.django_db

client = Client()


def test_200_response(section_page):
    "It should return 200 if section is valid"

    # section_page is created with a title of 'Section', so has a
    # slug of 'section':
    rv = client.get('/en/section/latest/')

    assert rv.status_code == 200


def test_invalid_sector_404s(section_page):
    "It should 404 if the sector_tag is invalid"

    rv = client.get('/en/nope/latest/')

    assert rv.status_code == 404


def test_context_data(section_page):
    "context data should be populated correctly"
    rv = client.get('/en/section/latest/')

    data = rv.context_data
    assert data['meta_title'] == 'Latest Section'
    assert isinstance(data['page'], SectionLatestPagesView)
    assert data['site_name'] == 'openownership.org'
    assert 'footer_nav' in data
    assert 'navbar_blocks' in data
    assert 'social_links' in data


def test_pages_live(section_page):
    "It should only include live pages"

    live = ArticlePage(live=True, title="Live")
    section_page.add_child(instance=live)
    live.save_revision().publish()

    draft = ArticlePage(live=False, title="Draft")
    section_page.add_child(instance=draft)
    live.save_revision()

    rv = client.get('/en/section/latest/')

    data = rv.context_data
    assert 'object_list' in data
    assert len(data['object_list']) == 1
    assert data['object_list'][0] == live


def test_pages_in_section(section_page):
    "It should only include pages in this section"

    article_1 = ArticlePage(live=True, title="Article 1")
    section_page.add_child(instance=article_1)
    article_1.save_revision().publish()

    grandparent = section_page.get_parent()

    section_2 = SectionPage(title="Section 2")
    grandparent.add_child(instance=section_2)
    section_2.save_revision().publish()
    article_2 = ArticlePage(live=True, title="Article 2")
    section_2.add_child(instance=article_2)
    article_2.save_revision().publish()

    rv = client.get('/en/section/latest/')

    data = rv.context_data
    assert 'object_list' in data
    assert len(data['object_list']) == 1
    assert data['object_list'][0] == article_1

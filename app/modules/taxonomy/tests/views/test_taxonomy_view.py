import pytest

from django.test import Client

from modules.content.models import (
    ArticlePage,
    BlogArticlePage,
    NewsArticlePage,
    JobPage,
    JobsIndexPage,
    NewsIndexPage,
    PublicationFrontPage,
    SectionPage,
)
from modules.taxonomy.models import PublicationType
from modules.taxonomy.views import TaxonomyView


# NOTE: Identical to test_focus_area_view.py except for using different tags and URLs.


pytestmark = pytest.mark.django_db

client = Client()


def test_200_response(section_page):
    "It should return 200 if sector and tag are valid"
    # section_page is created with a title of 'Section', so has a
    # slug of 'section':
    rv = client.get('/en/section/types/')

    assert rv.status_code == 200


def test_invalid_sector_404s(section_page):
    "It should 404 if the sector_tag is invalid"
    rv = client.get('/en/nope/types/')

    assert rv.status_code == 404


def test_invalid_taxonomy_404s(section_page):
    "It should 404 if the taxonomy_slug is invalid"
    rv = client.get('/en/section/nope/')

    assert rv.status_code == 404


def test_context_data(section_page):
    "context data should be populated correctly"
    PublicationType.objects.create(name='Cats')

    rv = client.get('/en/section/types/')

    data = rv.context_data
    assert data['meta_title'] == 'Publication type'
    assert isinstance(data['page'], TaxonomyView)
    assert data['site_name'] == 'openownership.org'
    assert 'footer_nav' in data
    assert 'navbar_blocks' in data
    assert 'social_links' in data


def test_tags_have_pages(blog_index_page):
    "It should only display tags that are used on pages"
    section_page = blog_index_page.get_parent()

    cats_category = PublicationType.objects.create(name='Cats')

    # Create a page with this category, so the category shows up:
    cats_post = BlogArticlePage(
        live=True, title="Cats post", publication_type=cats_category
    )
    section_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()

    # Shouldn't show up as it has no content:
    PublicationType.objects.create(name='Dogs')

    rv = client.get('/en/section/types/')

    data = rv.context_data
    assert 'pages' in data
    assert len(data['pages']) == 1
    assert data['pages'][0].title == 'Cats'
    assert data['pages'][0].url == "/en/section/types/cats/"


def test_tags_in_this_section(blog_index_page):
    "It should only display tags that are used on pages in this section"
    section_page = blog_index_page.get_parent()

    category = PublicationType.objects.create(name='Cats')

    # Create a page with this category, so the category shows up:
    cats_post = BlogArticlePage(
        live=True, title="Cats post", publication_type=category
    )
    section_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()

    grandparent = blog_index_page.get_parent().get_parent()

    # Make another section with a tagged News Article within it:

    section = SectionPage(title="Section 2")
    grandparent.add_child(instance=section)
    section.save_revision().publish()

    news_index_page = NewsIndexPage(title="News")
    section.add_child(instance=news_index_page)
    news_index_page.save_revision().publish()

    news_article = NewsArticlePage(live=True, title="News Article", publication_type=category)
    news_index_page.add_child(instance=news_article)
    news_article.save_revision().publish()

    rv = client.get('/en/section/types/')

    data = rv.context_data
    assert 'pages' in data
    assert len(data['pages']) == 1
    assert data['pages'][0].title == 'Cats'
    assert data['pages'][0].url == "/en/section/types/cats/"


def test_menu_pages(blog_index_page):
    "The correct data should be in the menu_pages context"
    section_page = blog_index_page.get_parent()

    cats_category = PublicationType.objects.create(name='Cats')

    # Create a page with this category, so the category shows up:
    cats_post = BlogArticlePage(
        live=True, title="Cats post", publication_type=cats_category
    )
    section_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()

    rv = client.get('/en/section/types/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 4

    assert pages[0]["page"].specific == section_page

    assert pages[1]["page"].title == "Area of Focus"
    assert pages[1]["page"].pk == "TaxonomyPagesView-section-FocusAreaTag"
    assert pages[1]["children"] == []

    assert pages[2]["page"].title == "Sector"
    assert pages[2]["page"].pk == "TaxonomyPagesView-section-SectorTag"
    assert pages[2]["children"] == []

    assert pages[3]["page"].title == "Publication type"
    assert pages[3]["page"].pk == "TaxonomyPagesView-section-PublicationType"
    assert len(pages[3]["children"]) == 1
    assert pages[3]["children"][0].title == "Cats"
    assert pages[3]["children"][0].pk == "TaxonomyPagesView-section-PublicationType-cats"
    assert pages[3]["children"][0].url == "/en/section/types/cats/"

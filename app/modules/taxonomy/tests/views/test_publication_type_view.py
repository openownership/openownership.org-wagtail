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
from modules.taxonomy.views import PublicationTypeView


# NOTE: Identical to test_focus_area_view.py except for using different tags and URLs.


pytestmark = pytest.mark.django_db

client = Client()


def test_200_response(section_page):
    "It should return 200 if sector and tag are valid"
    PublicationType.objects.create(name='Cats')

    # section_page is created with a title of 'Section', so has a
    # slug of 'section':
    rv = client.get('/en/section/types/cats/')

    assert rv.status_code == 200


def test_invalid_sector_404s(section_page):
    "It should 404 if the sector_tag is invalid"
    PublicationType.objects.create(name='Cats')

    rv = client.get('/en/nope/types/cats/')

    assert rv.status_code == 404


def test_invalid_tag_404s(section_page):
    "It should 404 if the tag_slug is invalid"

    rv = client.get('/en/section/types/cats/')

    assert rv.status_code == 404


def test_context_data(section_page):
    "context data should be populated correctly"
    tag = PublicationType.objects.create(name='Cats')

    rv = client.get('/en/section/types/cats/')

    data = rv.context_data
    assert data['tag'] == tag
    assert data['meta_title'] == 'Cats'
    assert isinstance(data['page'], PublicationTypeView)
    assert data['site_name'] == 'openownership.org'
    assert 'footer_nav' in data
    assert 'navbar_blocks' in data
    assert 'social_links' in data


def test_page_attributes(section_page):
    "The fake page attributes should work"
    PublicationType.objects.create(name='Cats')

    rv = client.get('/en/section/types/cats/')

    data = rv.context_data
    assert data['page'].title == 'Cats'
    assert data['page'].pk == 'TaxonomyView-section-PublicationType-cats'


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

    rv = client.get('/en/section/types/cats/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 4

    assert pages[0]["page"].specific == section_page

    assert pages[1]["page"].title == "Area of Focus"
    assert pages[1]["page"].pk == "TaxonomyView-section-FocusAreaTag"
    assert pages[1]["children"] == []

    assert pages[2]["page"].title == "Sector"
    assert pages[2]["page"].pk == "TaxonomyView-section-SectorTag"
    assert pages[2]["children"] == []

    assert pages[3]["page"].title == "Publication type"
    assert pages[3]["page"].pk == "TaxonomyView-section-PublicationType"
    assert len(pages[3]["children"]) == 1
    assert pages[3]["children"][0].title == "Cats"
    assert pages[3]["children"][0].pk == "TaxonomyView-section-PublicationType-cats"
    assert pages[3]["children"][0].url == "/en/section/types/cats/"


def test_queryset_tagged_pages(blog_index_page):
    "The queryset should only include pages with this category"
    cats_category = PublicationType.objects.create(name='Cats')
    dogs_category = PublicationType.objects.create(name='Dogs')

    cats_post = BlogArticlePage(
        live=True, title="Cats post", publication_type=cats_category
    )
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()

    dogs_post = BlogArticlePage(
        live=True, title="Dogs article", publication_type=dogs_category
    )
    blog_index_page.add_child(instance=dogs_post)
    dogs_post.save_revision().publish()

    rv = client.get('/en/section/types/cats/')

    data = rv.context_data
    assert len(data['object_list']) == 1
    assert data['object_list'][0].specific == cats_post


def test_queryset_live_pages(blog_index_page):
    "The queryset should only include live pages"
    category = PublicationType.objects.create(name='Cats')

    live_post = BlogArticlePage(
        live=True, title="Live post", publication_type=category
    )
    blog_index_page.add_child(instance=live_post)
    live_post.save_revision().publish()

    draft_post = BlogArticlePage(
        live=False, title="Draft post", publication_type=category
    )
    blog_index_page.add_child(instance=draft_post)
    draft_post.save_revision()

    # section_page, with slug of 'section' is the parent of blog_index_page
    rv = client.get('/en/section/types/cats/')

    data = rv.context_data
    assert len(data['object_list']) == 1
    assert data['object_list'][0].specific == live_post


def test_queryset_all_kinds_of_page(blog_index_page):
    "The queryset should include all kinds of pages with this tag"
    section_page = blog_index_page.get_parent()
    category = PublicationType.objects.create(name='Cats')

    # Make a couple more pages we need to make tagged pages under:

    jobs_index_page = JobsIndexPage(title="Jobs")
    section_page.add_child(instance=jobs_index_page)
    jobs_index_page.save_revision().publish()

    news_index_page = NewsIndexPage(title="News")
    section_page.add_child(instance=news_index_page)
    news_index_page.save_revision().publish()

    # Make all the tagged pages:

    blog_post = BlogArticlePage(
        live=True, title="Blog post", publication_type=category
    )
    blog_index_page.add_child(instance=blog_post)
    blog_post.save_revision().publish()

    news_article = NewsArticlePage(
        live=True, title="News post", publication_type=category
    )
    news_index_page.add_child(instance=news_article)
    news_article.save_revision().publish()

    job = JobPage(
        live=True, title="Job", publication_type=category
    )
    jobs_index_page.add_child(instance=job)
    job.save_revision().publish()

    publication = PublicationFrontPage(
        live=True, title="Publication", publication_type=category
    )
    section_page.add_child(instance=publication)
    publication.save_revision().publish()

    rv = client.get('/en/section/types/cats/')

    pages = [p.specific for p in rv.context_data['object_list']]
    assert len(pages) == 4
    assert blog_post in pages
    assert news_article in pages
    assert job in pages
    assert publication in pages


def test_queryset_order(blog_index_page):
    "The queryset should order by first_published_at descending"
    category = PublicationType.objects.create(name='Cats')

    post_1 = BlogArticlePage(
        live=True, title="Post 2", publication_type=category
    )
    blog_index_page.add_child(instance=post_1)
    post_1.save_revision().publish()

    post_2 = BlogArticlePage(
        live=True, title="Article 2", publication_type=category
    )
    blog_index_page.add_child(instance=post_2)
    post_2.save_revision().publish()

    post_3 = BlogArticlePage(
        live=True, title="Article 3", publication_type=category
    )
    blog_index_page.add_child(instance=post_3)
    post_3.save_revision().publish()

    rv = client.get('/en/section/types/cats/')

    pages = [p.specific for p in rv.context_data['object_list']]
    assert pages[0] == post_3
    assert pages[1] == post_2
    assert pages[2] == post_1


def test_queryset_section(blog_index_page):
    "The queryset should only include pages within this section"
    category = PublicationType.objects.create(name='Cats')

    post = BlogArticlePage(live=True, title="Post", publication_type=category)
    blog_index_page.add_child(instance=post)
    post.save_revision().publish()

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

    rv = client.get('/en/section/types/cats/')

    data = rv.context_data
    assert len(data['object_list']) == 1
    assert data['object_list'][0].specific == post

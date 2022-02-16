import pytest

from django.test import Client

from modules.content.models import (
    BlogArticlePage,
    NewsArticlePage,
    JobPage,
    JobsIndexPage,
    NewsIndexPage,
    PublicationFrontPage,
    SectionPage,
)
from modules.taxonomy.models import SectorTag, SectorTaggedPage


# NOTE: Identical to test_focus_area_view.py except for using different tags and URLs.


pytestmark = pytest.mark.django_db

client = Client()


def test_200_response(section_page):
    "It should return 200 if sector and tag are valid"
    SectorTag.objects.create(name='Cats')

    # section_page is created with a title of 'Section', so has a
    # slug of 'section':
    rv = client.get('/section/sector/cats/')

    assert rv.status_code == 200


def test_invalid_sector_404s(section_page):
    "It should 404 if the sector_tag is invalid"
    SectorTag.objects.create(name='Cats')

    rv = client.get('/nope/sector/cats/')

    assert rv.status_code == 404


def test_invalid_tag_404s(section_page):
    "It should 404 if the tag_slug is invalid"

    rv = client.get('/section/sector/cats/')

    assert rv.status_code == 404


def test_context_data(section_page):
    "context data should be populated correctly"
    tag = SectorTag.objects.create(name='Cats')

    rv = client.get('/section/sector/cats/')

    data = rv.context_data
    assert data['tag'] == tag
    assert data['meta_title'] == 'Cats'
    assert data['site_name'] == 'openownership.org'
    assert 'footer_nav' in data
    assert 'navbar_blocks' in data
    assert 'social_links' in data


def test_queryset_tagged_pages(blog_index_page):
    "The queryset should only include pages with this tag"
    cats_tag = SectorTag.objects.create(name='Cats')
    dogs_tag = SectorTag.objects.create(name='Dogs')

    cats_post = BlogArticlePage(live=True, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()
    SectorTaggedPage.objects.create(tag=cats_tag, content_object=cats_post)

    dogs_post = BlogArticlePage(live=True, title="Dogs post")
    blog_index_page.add_child(instance=dogs_post)
    dogs_post.save_revision().publish()
    SectorTaggedPage.objects.create(tag=dogs_tag, content_object=dogs_post)

    # section_page, with slug of 'section' is the parent of blog_index_page
    rv = client.get('/section/sector/cats/')

    data = rv.context_data
    assert len(data['object_list']) == 1
    assert data['object_list'][0].specific == cats_post


def test_queryset_live_pages(blog_index_page):
    "The queryset should only include live pages"
    tag = SectorTag.objects.create(name='Cats')

    live_post = BlogArticlePage(live=True, title="Live post")
    blog_index_page.add_child(instance=live_post)
    live_post.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=live_post)

    draft_post = BlogArticlePage(live=False, title="Draft post")
    blog_index_page.add_child(instance=draft_post)
    draft_post.save_revision()
    SectorTaggedPage.objects.create(tag=tag, content_object=draft_post)

    # section_page, with slug of 'section' is the parent of blog_index_page
    rv = client.get('/section/sector/cats/')

    data = rv.context_data
    assert len(data['object_list']) == 1
    assert data['object_list'][0].specific == live_post


def test_queryset_all_kinds_of_page(blog_index_page):
    "The queryset should include all kinds of pages with this tag"
    section_page = blog_index_page.get_parent()
    tag = SectorTag.objects.create(name='Cats')

    # Make a couple more pages we need to make tagged pages under:

    jobs_index_page = JobsIndexPage(title="Jobs")
    section_page.add_child(instance=jobs_index_page)
    jobs_index_page.save_revision().publish()

    news_index_page = NewsIndexPage(title="News")
    section_page.add_child(instance=news_index_page)
    news_index_page.save_revision().publish()

    # Make all the tagged pages:

    blog_post = BlogArticlePage(live=True, title="Blog post")
    blog_index_page.add_child(instance=blog_post)
    blog_post.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=blog_post)

    news_article = NewsArticlePage(live=True, title="News Article")
    news_index_page.add_child(instance=news_article)
    news_article.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=news_article)

    job = JobPage(live=True, title="Job")
    jobs_index_page.add_child(instance=job)
    job.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=job)

    publication = PublicationFrontPage(live=True, title="Publication")
    section_page.add_child(instance=publication)
    publication.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=publication)

    rv = client.get('/section/sector/cats/')

    pages = [p.specific for p in rv.context_data['object_list']]
    assert len(pages) == 4
    assert blog_post in pages
    assert news_article in pages
    assert job in pages
    assert publication in pages


def test_queryset_order(blog_index_page):
    "The queryset should order by first_published_at descending"
    tag = SectorTag.objects.create(name='Cats')

    post_1 = BlogArticlePage(live=True, title="Post 2")
    blog_index_page.add_child(instance=post_1)
    post_1.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=post_1)

    post_2 = BlogArticlePage(live=True, title="Post 2")
    blog_index_page.add_child(instance=post_2)
    post_2.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=post_2)

    post_3 = BlogArticlePage(live=True, title="Post 3")
    blog_index_page.add_child(instance=post_3)
    post_3.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=post_3)

    rv = client.get('/section/sector/cats/')

    pages = [p.specific for p in rv.context_data['object_list']]
    assert pages[0] == post_3
    assert pages[1] == post_2
    assert pages[2] == post_1


def test_queryset_section(blog_index_page):
    "The queryset should only include pages within this section"
    tag = SectorTag.objects.create(name='Cats')

    post = BlogArticlePage(live=True, title="Post")
    blog_index_page.add_child(instance=post)
    post.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=post)

    grandparent = blog_index_page.get_parent().get_parent()

    # Make another section with a tagged News Article within it:

    section = SectionPage(title="Section 2")
    grandparent.add_child(instance=section)
    section.save_revision().publish()

    news_index_page = NewsIndexPage(title="News")
    section.add_child(instance=news_index_page)
    news_index_page.save_revision().publish()

    news_article = NewsArticlePage(live=True, title="News Article")
    news_index_page.add_child(instance=news_article)
    news_article.save_revision().publish()
    SectorTaggedPage.objects.create(tag=tag, content_object=news_article)

    rv = client.get('/section/sector/cats/')

    data = rv.context_data
    assert len(data['object_list']) == 1
    assert data['object_list'][0].specific == post

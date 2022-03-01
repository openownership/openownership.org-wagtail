import pytest

from django.test import Client

from modules.content.models import ArticlePage, SectionListingPage


pytestmark = pytest.mark.django_db



def test_section_page_home(home_page):
    assert home_page.section_page is None


def test_section_page_section_page(section_page):
    assert section_page.section_page == section_page


def test_section_page_section_listing_page(section_listing_page):
    assert section_listing_page.section_page == section_listing_page


def test_section_page_blog_index_page(blog_index_page):
    assert blog_index_page.section_page.specific == blog_index_page.get_parent()


def test_section_page_blog_article(blog_article_page):
    assert blog_article_page.section_page.specific == blog_article_page.get_parent().get_parent()


def test_section_page_news_index_page(news_index_page):
    assert news_index_page.section_page.specific == news_index_page.get_parent()


def test_section_page_news_article(news_article_page):
    assert news_article_page.section_page.specific == news_article_page.get_parent().get_parent()


def test_section_page_jobs_index_page(jobs_index_page):
    assert jobs_index_page.section_page.specific == jobs_index_page.get_parent()


def test_section_page_job_page(job_page):
    assert job_page.section_page.specific == job_page.get_parent().get_parent()


def test_section_page_publication_front_page(publication_front_page):
    assert publication_front_page.section_page.specific == publication_front_page.get_parent()


def test_section_page_publication_inner_page(publication_inner_page):
    assert publication_inner_page.section_page.specific == publication_inner_page.get_parent().get_parent()

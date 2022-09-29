# 3rd party
import pytest
import arrow
from wagtail.models import Page

from modules.settings.models.site_settings import SiteSettings
from modules.content.models import (
    ArticlePage,
    Author,
    HomePage,
    BlogArticlePage,
    BlogArticleAuthorRelationship,
    BlogIndexPage,
    GlossaryPage,
    JobsIndexPage,
    JobPage,
    NewsArticlePage,
    NewsArticleAuthorRelationship,
    NewsIndexPage,
    PressLink,
    PublicationFrontPage,
    PublicationAuthorRelationship,
    PublicationInnerPage,
    SectionListingPage,
    SectionPage,
    TagPage,
    TaxonomyPage,
    TeamPage,
    TeamProfilePage,
)


pytestmark = pytest.mark.django_db


########################################################################
# Private creation functions


def _create_article_page(
    title: str, parent: Page, modifier: int = 1
) -> ArticlePage:
    p = ArticlePage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_blog_article_page(
    title: str, parent: Page, modifier: int = 1
) -> BlogArticlePage:
    p = BlogArticlePage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_blog_index_page(
    title: str, parent: Page, modifier: int = 1
) -> BlogIndexPage:
    p = BlogIndexPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_home_page(title, parent):
    p = HomePage()
    p.first_published_at = arrow.now().datetime
    p.title = title
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_glossary_page(
    title: str, parent: Page, modifier: int = 1
) -> GlossaryPage:
    p = GlossaryPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_jobs_index_page(
    title: str, parent: Page, modifier: int = 1
) -> JobsIndexPage:
    p = JobsIndexPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_job_page(
    title: str, parent: Page, modifier: int = 1
) -> JobPage:
    p = JobPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_news_article_page(
    title: str, parent: Page, modifier: int = 1
) -> NewsArticlePage:
    p = NewsArticlePage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_news_index_page(
    title: str, parent: Page, modifier: int = 1
) -> NewsIndexPage:
    p = NewsIndexPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_publication_front_page(
    title: str, parent: Page, modifier: int = 1
) -> PublicationFrontPage:
    p = PublicationFrontPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_publication_inner_page(
    title: str, parent: Page, modifier: int = 1
) -> PublicationInnerPage:
    p = PublicationInnerPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_section_listing_page(
    title: str, parent: Page, modifier: int = 1
) -> SectionListingPage:
    p = SectionListingPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_section_page(
    title: str, parent: Page, modifier: int = 1
) -> SectionPage:
    p = SectionPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_tag_page(
    title: str, parent: Page, modifier: int = 1
) -> TagPage:
    p = TagPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_taxonomy_page(
    title: str, parent: Page, modifier: int = 1
) -> TaxonomyPage:
    p = TaxonomyPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_team_page(
    title: str, parent: Page, modifier: int = 1
) -> TeamPage:
    p = TeamPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_team_profile_page(
    title: str, parent: Page, modifier: int = 1
) -> TeamProfilePage:
    p = TeamProfilePage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


########################################################################
# Fixtures for Pages


@pytest.fixture(scope="function")
def article_page(section_listing_page):
    p = _create_article_page("Article", section_listing_page)
    return p


@pytest.fixture(scope="function")
def blog_article_page(blog_index_page):
    p = _create_blog_article_page("Blog Article", blog_index_page)
    return p


@pytest.fixture(scope="function")
def blog_index_page(section_page):
    p = _create_blog_index_page("Blog Index", section_page)
    return p


@pytest.fixture(scope="function")
def home_page(site_root):
    p = _create_home_page("Test Site Home", site_root)
    return p


@pytest.fixture(scope="function")
def site_settings(site):
    settings, created = SiteSettings.objects.get_or_create(site_id=site.id)
    settings.save()
    return settings


@pytest.fixture(scope="function")
def glossary_page(section_page):
    p = _create_glossary_page("Glossary", section_page)
    return p


@pytest.fixture(scope="function")
def jobs_index_page(section_listing_page):
    p = _create_jobs_index_page("Job Index", section_listing_page)
    return p


@pytest.fixture(scope="function")
def job_page(jobs_index_page):
    p = _create_job_page("Job", jobs_index_page)
    return p


@pytest.fixture(scope="function")
def news_article_page(news_index_page):
    p = _create_news_article_page("News Article", news_index_page)
    return p


@pytest.fixture(scope="function")
def news_index_page(section_page):
    p = _create_news_index_page("News Index", section_page)
    return p


@pytest.fixture(scope="function")
def publication_front_page(section_page):
    p = _create_publication_front_page("Publication", section_page)
    return p


@pytest.fixture(scope="function")
def publication_inner_page(publication_front_page):
    p = _create_publication_inner_page("Publication Inner", publication_front_page)
    return p


@pytest.fixture(scope="function")
def section_listing_page(home_page):
    p = _create_section_listing_page("Section Listing", home_page)
    return p


@pytest.fixture(scope="function")
def section_page(home_page):
    p = _create_section_page("Section", home_page)
    return p


@pytest.fixture(scope="function")
def tag_page(taxonomy_page):
    p = _create_tag_page("Tag", taxonomy_page)
    return p


@pytest.fixture(scope="function")
def taxonomy_page(home_page):
    p = _create_taxonomy_page("Taxonomy", home_page)
    return p


@pytest.fixture(scope="function")
def team_page(section_listing_page):
    p = _create_team_page("Team", section_listing_page)
    return p


@pytest.fixture(scope="function")
def team_profile_page(team_page):
    p = _create_team_profile_page("Team Profile", team_page)
    return p


@pytest.fixture(scope="function")
def site_root():
    return Page.objects.filter(path="0001").first()


########################################################################
# Fixtures for Snippets


@pytest.fixture(scope="function")
def author():
    return Author.objects.create(name="Bob Ferris")


@pytest.fixture(scope="function")
def author_with_blog_articles(author, blog_index_page):
    "An author with six live blog articles"

    for n in range(1, 7):
        p = BlogArticlePage(live=True, title=f"Article {n}")
        p.first_published_at = arrow.now().shift(days=-n).datetime
        blog_index_page.add_child(instance=p)
        p.save_revision().publish()
        BlogArticleAuthorRelationship(page=p, author=author).save()

    return author


@pytest.fixture(scope="function")
def author_with_news_articles(author, news_index_page):
    "An author with six live news articles"

    for n in range(1, 7):
        p = NewsArticlePage(live=True, title=f"Article {n}")
        p.first_published_at = arrow.now().shift(days=-n).datetime
        news_index_page.add_child(instance=p)
        p.save_revision().publish()
        NewsArticleAuthorRelationship(page=p, author=author).save()

    return author


@pytest.fixture(scope="function")
def author_with_publications(author, section_page):
    "An author with six live publications"

    for n in range(1, 7):
        p = PublicationFrontPage(live=True, title=f"Publication {n}")
        p.first_published_at = arrow.now().shift(days=-n).datetime
        section_page.add_child(instance=p)
        p.save_revision().publish()
        PublicationAuthorRelationship(page=p, author=author).save()

    return author


@pytest.fixture(scope="function")
def author_with_content_pages(author, blog_index_page, news_index_page, section_page):
    "An author with 2 live blog articles, 2 live news articles and 2 live publications"

    for n in range(1, 3):
        p = BlogArticlePage(live=True, title=f"Blog Article {n}")
        p.first_published_at = arrow.now().shift(days=-n).datetime
        blog_index_page.add_child(instance=p)
        p.save_revision().publish()
        BlogArticleAuthorRelationship(page=p, author=author).save()

    for n in range(1, 3):
        p = NewsArticlePage(live=True, title=f"News Article {n}")
        # Timed to be after the last blog article:
        p.first_published_at = arrow.now().shift(days=-(2 + n)).datetime
        news_index_page.add_child(instance=p)
        p.save_revision().publish()
        NewsArticleAuthorRelationship(page=p, author=author).save()

    for n in range(1, 3):
        p = PublicationFrontPage(live=True, title=f"Publication {n}")
        # Timed to be after the last news article:
        p.first_published_at = arrow.now().shift(days=-(4 + n)).datetime
        section_page.add_child(instance=p)
        p.save_revision().publish()
        PublicationAuthorRelationship(page=p, author=author).save()

    return author



@pytest.fixture(scope="function")
def press_link():
    return PressLink.objects.create(title="Press Link", url="https://example.org/foo/")

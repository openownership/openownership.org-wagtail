import pytest

from modules.content.models import (
    BlogArticleAuthorRelationship,
    BlogArticlePage,
    NewsArticleAuthorRelationship,
    NewsArticlePage,
    PublicationFrontPage,
    PublicationAuthorRelationship,
)


########################################################################
# Author.get_blog_articles()


def test_get_blog_articles_num_default(author_with_blog_articles):
    "It should return the 5 most recent articles by default"
    articles = author_with_blog_articles.get_blog_articles()
    assert len(articles) == 5
    assert articles[0].title == "Article 1"
    assert articles[1].title == "Article 2"
    assert articles[2].title == "Article 3"
    assert articles[3].title == "Article 4"
    assert articles[4].title == "Article 5"


def test_get_blog_articles_num_specified(author_with_blog_articles):
    "It should return the number of articles requested"
    articles = author_with_blog_articles.get_blog_articles(num=3)
    assert len(articles) == 3


def test_get_blog_articles_live_only(author, blog_index_page):
    "It should not return non-live articles"
    p = BlogArticlePage(live=False, title="Article")
    blog_index_page.add_child(instance=p)
    p.save_revision()
    BlogArticleAuthorRelationship(page=p, author=author).save()
    assert len(author.get_blog_articles()) == 0


########################################################################
# Author.get_news_articles()


def test_get_news_articles_num_default(author_with_news_articles):
    "It should return the 5 most recent articles by default"
    articles = author_with_news_articles.get_news_articles()
    assert len(articles) == 5
    assert articles[0].title == "Article 1"
    assert articles[1].title == "Article 2"
    assert articles[2].title == "Article 3"
    assert articles[3].title == "Article 4"
    assert articles[4].title == "Article 5"


def test_get_news_articles_num_specified(author_with_news_articles):
    "It should return the number of articles requested"
    articles = author_with_news_articles.get_news_articles(num=3)
    assert len(articles) == 3


def test_get_news_articles_live_only(author, news_index_page):
    "It should not return non-live articles"
    p = NewsArticlePage(live=False, title="Article")
    news_index_page.add_child(instance=p)
    p.save_revision()
    NewsArticleAuthorRelationship(page=p, author=author).save()
    assert len(author.get_news_articles()) == 0



########################################################################
# Author.get_publiations()


def test_get_publications_num_default(author_with_publications):
    "It should return the 5 most recent publications by default"
    publications = author_with_publications.get_publications()
    assert len(publications) == 5
    assert publications[0].title == "Publication 1"
    assert publications[1].title == "Publication 2"
    assert publications[2].title == "Publication 3"
    assert publications[3].title == "Publication 4"
    assert publications[4].title == "Publication 5"


def test_get_news_publications_num_specified(author_with_publications):
    "It should return the number of publications requested"
    publications = author_with_publications.get_publications(num=3)
    assert len(publications) == 3


def test_get_news_publications_live_only(author, section_page):
    "It should not return non-live publications"
    p = PublicationFrontPage(live=False, title="Publication")
    section_page.add_child(instance=p)
    p.save_revision()
    PublicationAuthorRelationship(page=p, author=author).save()
    assert len(author.get_publications()) == 0


########################################################################
# Author.get_content_pages()


def test_get_content_pages(author_with_content_pages):
    "It should return the 5 most recent content pages by default"
    pages = author_with_content_pages.get_content_pages()
    assert len(pages) == 5
    assert pages[0].title == "Blog Article 1"
    assert pages[1].title == "Blog Article 2"
    assert pages[2].title == "News Article 1"
    assert pages[3].title == "News Article 2"
    assert pages[4].title == "Publication 1"


def test_get_content_pages_num_specified(author_with_content_pages):
    "It should return the number of pages requested"
    articles = author_with_content_pages.get_content_pages(num=3)
    assert len(articles) == 3


def test_get_content_pages_live_only(author, blog_index_page, news_index_page, section_page):
    "It should not return non-live content pages"
    p = BlogArticlePage(live=False, title="Blog Article")
    blog_index_page.add_child(instance=p)
    p.save_revision()
    BlogArticleAuthorRelationship(page=p, author=author).save()

    p = NewsArticlePage(live=False, title="News Article")
    news_index_page.add_child(instance=p)
    p.save_revision()
    NewsArticleAuthorRelationship(page=p, author=author).save()

    p = PublicationFrontPage(live=False, title="Publication")
    section_page.add_child(instance=p)
    p.save_revision()
    PublicationAuthorRelationship(page=p, author=author).save()

    assert len(author.get_content_pages()) == 0

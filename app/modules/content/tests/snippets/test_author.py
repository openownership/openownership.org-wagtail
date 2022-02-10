import pytest

from modules.content.models import (
    BlogArticleAuthorRelationship,
    BlogArticlePage,
    NewsArticleAuthorRelationship,
    NewsArticlePage,
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
# Author.get_content_pages()


def test_get_content_pages(author_with_content_pages):
    "It should return the 5 most recent content pages by default"
    pages = author_with_content_pages.get_content_pages()
    assert len(pages) == 5
    assert pages[0].title == "Blog Article 1"
    assert pages[1].title == "Blog Article 2"
    assert pages[2].title == "Blog Article 3"
    assert pages[3].title == "News Article 1"
    assert pages[4].title == "News Article 2"


def test_get_content_pages_num_specified(author_with_content_pages):
    "It should return the number of pages requested"
    articles = author_with_content_pages.get_content_pages(num=3)
    assert len(articles) == 3


def test_get_content_pages_live_only(author, blog_index_page, news_index_page):
    "It should not return non-live content pages"
    p = BlogArticlePage(live=False, title="Blog Article")
    blog_index_page.add_child(instance=p)
    p.save_revision()
    BlogArticleAuthorRelationship(page=p, author=author).save()

    p = NewsArticlePage(live=False, title="News Article")
    news_index_page.add_child(instance=p)
    p.save_revision()
    NewsArticleAuthorRelationship(page=p, author=author).save()

    assert len(author.get_content_pages()) == 0

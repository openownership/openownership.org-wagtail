import json
import arrow
import pytest

from modules.content.tests.data import RICH_TEXT


def test_search_description(client, blog_article_page):
    page = blog_article_page
    page.search_description = "This is the search description"
    page.save_revision().publish()
    res = client.get(page.url)
    assert "This is the search description" in res.rendered_content


def test_blurb(client, blog_article_page):
    page = blog_article_page
    page.blurb = "This is the blurb"
    page.save_revision().publish()
    res = client.get(page.url)
    assert "This is the blurb" in res.rendered_content


def test_page_content(client, blog_article_page):
    page = blog_article_page
    page.body = json.dumps([RICH_TEXT])
    page.save_revision().publish()
    res = client.get(page.url)
    assert '''<meta name="description" content="Donec ullamcorper nulla non metus auctor fringilla.
        Etiam porta sem malesuada magna mollis euismod. Maecenas sed diam eget risus varius
        blandit sit amet non magna. Sed posuere..." />''' in res.rendered_content


def test_site_wide_meta(client, blog_article_page, site_settings):
    page = blog_article_page
    site_settings.meta_description = "This is the sitewide meta description"
    site_settings.save()
    res = client.get(page.url)
    assert "This is the sitewide meta description" in res.rendered_content


def test_page_content_overrides_site_wide_meta(client, blog_article_page, site_settings):
    page = blog_article_page
    site_settings.meta_description = "This is the sitewide meta description"
    site_settings.save()
    page.body = json.dumps([RICH_TEXT])
    page.save_revision().publish()
    res = client.get(page.url)
    assert "This is the sitewide meta description" not in res.rendered_content
    assert '''<meta name="description" content="Donec ullamcorper nulla non metus auctor fringilla.
        Etiam porta sem malesuada magna mollis euismod. Maecenas sed diam eget risus varius
        blandit sit amet non magna. Sed posuere..." />''' in res.rendered_content


def test_blurb_overrides_both(client, blog_article_page, site_settings):
    page = blog_article_page
    site_settings.meta_description = "This is the sitewide meta description"
    site_settings.save()
    page.body = json.dumps([RICH_TEXT])
    page.blurb = "This is the blurb"
    page.save_revision().publish()
    res = client.get(page.url)
    assert "This is the sitewide meta description" not in res.rendered_content
    assert '''<meta name="description" content="Donec ullamcorper nulla non metus auctor fringilla.
        Etiam porta sem malesuada magna mollis euismod. Maecenas sed diam eget risus varius
        blandit sit amet non magna. Sed posuere..." />''' not in res.rendered_content
    assert "This is the blurb" in res.rendered_content


def test_search_description_overrides_all(client, blog_article_page, site_settings):
    page = blog_article_page
    site_settings.meta_description = "This is the sitewide meta description"
    site_settings.save()
    page.body = json.dumps([RICH_TEXT])
    page.search_description = "This is the search description"
    page.blurb = "This is the blurb"
    page.save_revision().publish()
    res = client.get(page.url)
    assert "This is the sitewide meta description" not in res.rendered_content
    assert '''<meta name="description" content="Donec ullamcorper nulla non metus auctor fringilla.
        Etiam porta sem malesuada magna mollis euismod. Maecenas sed diam eget risus varius
        blandit sit amet non magna. Sed posuere..." />''' not in res.rendered_content
    assert "This is the blurb" not in res.rendered_content
    assert "This is the search description" in res.rendered_content

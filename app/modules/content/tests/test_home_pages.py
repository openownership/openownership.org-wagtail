import pytest

from django.test import Client


pytestmark = pytest.mark.django_db

client = Client()


def test_home_page_gets_created(home_page):
    assert home_page is not None
    assert home_page.title == "Test Site Home"


def test_home_page_200s(home_page):
    assert home_page.url == "/test-site-home/"
    response = client.get(home_page.url)
    assert response.status_code == 200


def test_home_page_context(home_page):
    "Correct values should be in the context"
    home_page.hero_headline = "<p>Hi</p>"
    home_page.save_revision().publish()

    response = client.get(home_page.url)
    assert response.context_data["body_classes"] == "home-page"
    assert response.context_data["is_home"] is True
    assert response.context_data["has_hero"] is True


def test_home_page_hero(home_page):
    "Text in the hero's fields should be in the rendered content"
    headline = '<p><b>Hello</b></p><p>World</p>'
    body = '<p>Some text <i>here</i>.</p>'
    home_page.hero_headline = headline
    home_page.hero_body = body
    home_page.save_revision().publish()

    response = client.get(home_page.url)
    assert headline in response.rendered_content
    assert body in response.rendered_content

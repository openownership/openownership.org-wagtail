import pytest

from django.test import Client


client = Client()


def test_show_sharing_buttons_true(utility_page):
    utility_page.show_sharing_buttons = True
    utility_page.save_revision().publish()
    res = client.get(utility_page.url)
    assert '<div class="share-page">' in res.rendered_content


def test_show_sharing_buttons_false(utility_page):
    utility_page.show_sharing_buttons = False
    utility_page.save_revision().publish()
    res = client.get(utility_page.url)
    assert '<div class="share-page">' not in res.rendered_content

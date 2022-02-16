import json
import pytest
from django.test import Client
from modules.settings.tests.blocks import NAV_ITEM_PAGE, NAV_ITEM_URL


pytestmark = pytest.mark.django_db

client = Client()


def test_nav_item_page(home_page, nav_settings):
    p = home_page
    data = NAV_ITEM_PAGE
    data['value']['link_page'] = home_page.id
    nav_settings.footer_nav = json.dumps([
        data
    ])
    nav_settings.save()
    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "Link to home page" in rv.rendered_content


def test_nav_item_url(home_page, nav_settings):
    p = home_page
    data = NAV_ITEM_URL
    nav_settings.footer_nav = json.dumps([
        data
    ])
    nav_settings.save()
    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "Find a centre" in rv.rendered_content

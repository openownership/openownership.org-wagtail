import json
import pytest
from django.test import Client
from modules.settings.tests.blocks import NAV_ITEM_PAGE, NAV_ITEM_URL, MEGA_MENU


pytestmark = pytest.mark.django_db

client = Client()


def test_nav_item_page(home_page, nav_settings):
    p = home_page
    data = NAV_ITEM_PAGE
    data['value']['link_page'] = home_page.id
    nav_settings.navbar_blocks = json.dumps([
        data
    ])
    nav_settings.save()
    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "Link to home page" in rv.rendered_content


def test_nav_item_url(home_page, nav_settings):
    p = home_page
    data = NAV_ITEM_URL
    nav_settings.navbar_blocks = json.dumps([
        data
    ])
    nav_settings.save()
    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "Find a centre" in rv.rendered_content


def test_meganav(home_page, nav_settings):
    p = home_page
    data = MEGA_MENU
    data['value']['objects'][0]['links'][0]['link_page'] = home_page.id
    nav_settings.navbar_blocks = json.dumps([
        data
    ])
    nav_settings.save()
    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "Get help" in rv.rendered_content
    assert "Not sure where to start?" in rv.rendered_content
    assert "Link to home page" in rv.rendered_content
    assert "Link to live chat" in rv.rendered_content
    assert "Tools to help you cope" in rv.rendered_content
    assert "Find a centre" in rv.rendered_content

import json
import pytest
from cacheops import CacheMiss, cache
from django.test import Client
from wagtail.models import Site
from modules.settings.models import NavigationSettings
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


def test_stale_empty_nav_cache_is_not_served(home_page, nav_settings, monkeypatch):
    from modules.settings.models import navigation_settings as ns_mod

    p = home_page
    data = NAV_ITEM_URL
    nav_settings.navbar_blocks = json.dumps([
        data
    ])
    nav_settings.save()

    # Simulate a poisoned cache holding an empty menu, as happens when it was
    # first built before the nav was configured. The configured menu must still
    # render rather than the stale empty one.
    key = NavigationSettings.get_cache_key_nav(Site.objects.first().pk)
    poison = {'navbar_blocks': [], 'footer_nav': [], 'footer_nav2': []}

    def fake_get(k):
        if k == key:
            return poison
        raise CacheMiss

    monkeypatch.setattr(ns_mod.cache, 'get', fake_get)
    monkeypatch.setattr(ns_mod.cache, 'set', lambda *a, **k: None)

    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "Find a centre" in rv.rendered_content


def test_meganav(home_page, nav_settings):
    p = home_page
    data = MEGA_MENU
    data['value']['nav_item']['link_page'] = home_page.id
    nav_settings.navbar_blocks = json.dumps([
        data
    ])
    nav_settings.save()
    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "Link to home page" in rv.rendered_content
    assert "Tools to help you cope" in rv.rendered_content
    assert "Link to live chat" in rv.rendered_content
    assert "Find a centre" in rv.rendered_content

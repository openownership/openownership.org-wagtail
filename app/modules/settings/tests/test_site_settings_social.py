import json
import pytest
from django.test import Client
from modules.settings.models import SiteSettings
from modules.settings.tests.blocks import SOCIAL_LINKS


pytestmark = pytest.mark.django_db

client = Client()


def test_social_links(home_page, site_settings):
    p = home_page
    data = SOCIAL_LINKS
    site_settings.accounts = json.dumps([
        data
    ])
    site_settings.save()
    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "twitter" in rv.rendered_content


def test_stale_empty_social_cache_is_not_served(site, site_settings, monkeypatch):
    from modules.settings.models import mixins as mixins_mod

    site_settings.social_accounts = json.dumps([
        SOCIAL_LINKS
    ])
    site_settings.save()

    # Simulate a poisoned cache holding no social links, as happens when it was
    # first built before any accounts were added. The configured links must still
    # be returned rather than the stale empty ones.
    key = SiteSettings.get_cache_key_social(site.pk)
    poison = {'social_links': {}}
    orig_get = mixins_mod.cache.get

    def fake_get(k, *args, **kwargs):
        if k == key:
            return poison
        return orig_get(k, *args, **kwargs)

    monkeypatch.setattr(mixins_mod.cache, 'get', fake_get)
    monkeypatch.setattr(mixins_mod.cache, 'set', lambda *a, **k: None)

    ctx = SiteSettings.get_social_context(site)
    assert ctx['social_links']
    assert 'https://www.twitter.com' in ctx['social_links'].values()

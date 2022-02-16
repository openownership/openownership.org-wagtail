import json
import pytest
from django.test import Client
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

import pytest
from django.test import Client


pytestmark = pytest.mark.django_db

client = Client()


def test_metatags(home_page, site_settings, site_image):
    p = home_page
    site_settings.meta_description = 'Get information, help and support'
    site_settings.meta_image = site_image
    site_settings.save()
    rv = client.get(p.url)
    assert rv.status_code == 200
    assert "Get information, help and support" in rv.rendered_content
    assert "/media/images/test_" in rv.rendered_content

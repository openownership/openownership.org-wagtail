import os
import pytest
import unittest.mock
from django.test import Client


pytestmark = pytest.mark.django_db

client = Client()


def test_site_created(site):
    assert site is not None


def test_site_settings_created(site_settings):
    assert site_settings is not None


def test_root_page_created(site_root):
    assert site_root is not None


def test_home_page_created(home_page):
    assert home_page is not None


@unittest.mock.patch.dict('os.environ', {'SERVER_ENV': 'production'})
def test_analytics(home_page, site_settings):
    """
    In order to get the analytics properties to show on the
    home page, we need to mock the production environment
    """
    p = home_page
    site_settings.analytics_property_id = 'UA-TEST'
    site_settings.tag_manager_property_id = 'GTMTEST'
    site_settings.save()
    rv = client.get(p.url)
    test_env = os.getenv("SERVER_ENV")
    assert rv.status_code == 200
    assert test_env == "production"
    assert "UA-TEST" and "GTMTEST" in rv.rendered_content

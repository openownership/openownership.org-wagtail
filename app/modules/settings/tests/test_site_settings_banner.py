# import pytest
# from django.test import Client


# pytestmark = pytest.mark.django_db

# client = Client()


# def test_update_banner_all_pages(home_page, site_settings):
#     p = home_page
#     site_settings.body = 'Look at this update banner'
#     site_settings.link_page = home_page
#     site_settings.link_label = 'Link to home page'
#     site_settings.live = True
#     site_settings.show_on_all_pages = True
#     site_settings.save()
#     rv = client.get(p.url)
#     assert rv.status_code == 200
#     assert "Look at this update banner" in rv.rendered_content
#     assert "Link to home page" in rv.rendered_content


# def test_update_banner_home_page(home_page, site_settings):
#     p = home_page
#     site_settings.body = 'Look at this update banner'
#     site_settings.link_page = home_page
#     site_settings.link_label = 'Link to home page'
#     site_settings.live = True
#     site_settings.show_on_all_pages = False
#     site_settings.limit_to_pages.set([home_page])
#     site_settings.save()
#     rv = client.get(p.url)
#     assert rv.status_code == 200
#     assert "Look at this update banner" in rv.rendered_content
#     assert "Link to home page" in rv.rendered_content

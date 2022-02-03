# 3rd party
import pytest
import arrow
from wagtail.core.models import Page

from modules.content.models import HomePage, SectionListingPage


pytestmark = pytest.mark.django_db


def _create_home_page(title, parent):
    p = HomePage()
    p.first_published_at = arrow.now().datetime
    p.title = title
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_section_listing_page(
    title: str, parent: Page, modifier: int = 1
) -> SectionListingPage:
    p = SectionListingPage()
    p.title = title
    p.first_published_at = arrow.now().shift(days=modifier * -1).datetime
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


@pytest.fixture(scope="function")
def site_root():
    return Page.objects.filter(path="0001").first()


@pytest.fixture(scope="function")
def home_page(site_root):
    p = _create_home_page("Test Site Home", site_root)
    return p


@pytest.fixture(scope="function")
def section_listing_page(home_page):
    p = _create_section_listing_page("Section Listing", home_page)
    return p

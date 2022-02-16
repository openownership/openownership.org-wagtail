import arrow
import pytest
import random
from modules.content.models import HomePage
from modules.core.models import SiteImage
from modules.settings.models import NavigationSettings, SiteSettings
from wagtail.core.models import Page, Site
from wagtail.images.tests.utils import get_test_image_file


pytestmark = pytest.mark.django_db


def _create_home_page(title, parent):
    p = HomePage()
    p.first_published_at = arrow.now().datetime
    p.title = title
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


def _create_image():
    f = get_test_image_file()
    img = SiteImage(
        collection_id=1,
        title='Site image',
        file=f,
        width=50,
        height=50,
        created_at=arrow.now().datetime,
        file_size=random.randint(1, 9999),
        alt_text="Site image alt text"
    )
    img.save()
    return img


@pytest.fixture(scope="function")
def site():
    return Site.objects.first()


@pytest.fixture(scope="function")
def site_root():
    return Page.objects.filter(path='0001').first()


@pytest.fixture(scope="function")
def home_page(site_root):
    return _create_home_page('Test Site Home', site_root)


@pytest.fixture(scope="function")
def site_image():
    return _create_image()


@pytest.fixture(scope="function")
def site_settings(site):
    settings, created = SiteSettings.objects.get_or_create(site_id=site.id)
    settings.save()
    return settings


@pytest.fixture(scope="function")
def nav_settings(site):
    settings, created = NavigationSettings.objects.get_or_create(site_id=site.id)
    settings.save()
    return settings

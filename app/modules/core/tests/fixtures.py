# 3rd party
import pytest
import arrow
from wagtail.core.models import Page

from ..models import HomePage


pytestmark = pytest.mark.django_db


def _create_home_page(title, parent):
    p = HomePage()
    p.first_published_at = arrow.now().datetime
    p.title = title
    parent.add_child(instance=p)
    p.save_revision().publish()
    return p


@pytest.fixture(scope="function")
def site_root():
    return Page.objects.filter(path='0001').first()


@pytest.fixture(scope="function")
def home_page(site_root):
    p = _create_home_page('Test Site Home', site_root)
    return p

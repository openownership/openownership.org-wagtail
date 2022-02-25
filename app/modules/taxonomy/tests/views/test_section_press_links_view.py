import pytest

from django.test import Client

from modules.content.models import (
    SectionPage,
)
from modules.content.models import PressLink


pytestmark = pytest.mark.django_db

client = Client()


def test_200_response(section_page):
    "It should return 200 if sector and tag are valid"
    # section_page is created with a title of 'Section', so has a
    # slug of 'section':
    rv = client.get('/en/section/press-links/')

    assert rv.status_code == 200


def test_invalid_sector_404s(section_page):
    "It should 404 if the sector_tag is invalid"
    rv = client.get('/en/nope/press-links/')

    assert rv.status_code == 404


def test_pages_in_section(section_page):
    "It should only include pages in this section"

    link_1 = PressLink.objects.create(title="Link 1", section_page=section_page)

    grandparent = section_page.get_parent()

    section_2 = SectionPage(title="Section 2")
    grandparent.add_child(instance=section_2)
    section_2.save_revision().publish()

    PressLink.objects.create(title="Link 2", section_page=section_2)

    rv = client.get('/en/section/press-links/')

    data = rv.context_data
    assert 'object_list' in data
    assert len(data['object_list']) == 1
    assert data['object_list'][0] == link_1

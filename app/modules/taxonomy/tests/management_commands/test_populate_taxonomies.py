import pytest

from django.core.management import call_command

from modules.taxonomy.models import FocusAreaTag, PublicationType, SectorTag


pytestmark = pytest.mark.django_db


def test_populates_areas_of_focus():
    "It should create all the FocusAreaTags"
    call_command('populate_taxonomies', verbosity=0)

    valid_names = [
        'Law',
        'Policy',
        'Systems & data',
    ]

    tags = FocusAreaTag.objects.all()

    assert len(tags) == 3
    assert valid_names == [t.name for t in tags]


def test_populates_publication_types():
    "It should create all the PublicationTypes"
    call_command('populate_taxonomies', verbosity=0)

    valid_names = [
        "Job",
        "Blog post",
        "Briefing",
        "Case study",
        "Event",
        "Forms",
        "Guidance",
        "News article",
        "Publication",
        "Technical guidance",
        "Tools",
        "Video",
    ]

    types = PublicationType.objects.all()

    assert len(types) == 12
    assert valid_names == [t.name for t in types]


def test_populates_sectors():
    "It should create all the Sectors"
    call_command('populate_taxonomies', verbosity=0)

    valid_names = [
        'Banking',
        'Environment',
        'Extractives',
    ]

    tags = SectorTag.objects.all()

    assert len(tags) == 3
    assert valid_names == [t.name for t in tags]

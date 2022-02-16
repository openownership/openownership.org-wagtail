import arrow
import pytest

from django.core.management import call_command

from modules.content.models import JobPage
from modules.taxonomy.models import PublicationType


def test_human_display_date(job_page):
    "It should return the display date in correct format"
    dt = arrow.get("2022-01-09 12:00:00").datetime
    job_page.display_date = dt
    assert job_page.human_display_date == "09 January 2022"


def test_human_application_deadline(job_page):
    "It should return the application_deadline in correct format"
    dt = arrow.get("2022-01-09 12:00:00").datetime
    job_page.application_deadline = dt
    assert job_page.human_application_deadline == "09 January 2022"


def test_publication_type_choices(job_page):
    "It should return the only PublicationTypes availeble to this page"
    call_command('populate_taxonomies', verbosity=0)

    types = job_page.get_publication_type_choices()

    assert len(types) == 1
    assert isinstance(types[0], PublicationType)
    assert types[0].name == "Job"

import pytest

from django.test import Client

from modules.content.models import JobsIndexPage, JobPage


pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_self(job_index_page):
    "Should include itself in the menu_pages"

    rv = client.get(job_index_page.url)

    pages = [p.specific for p in rv.context_data["menu_pages"]]
    assert job_index_page in pages


def test_menu_pages_live(job_index_page):
    "Should only include live pages, not draft ones"

    live_job = JobPage(live=True, title="Live")
    job_index_page.add_child(instance=live_job)

    draft_job = JobPage(live=False, title="Live")
    job_index_page.add_child(instance=draft_job)

    rv = client.get(job_index_page.url)

    pages = [p.specific for p in rv.context_data["menu_pages"]]
    assert live_job in pages
    assert draft_job not in pages

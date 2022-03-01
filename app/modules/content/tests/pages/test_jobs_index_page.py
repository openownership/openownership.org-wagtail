import pytest

from django.test import Client

from modules.content.models import JobsIndexPage, JobPage


pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_self(jobs_index_page):
    "Should include itself in the menu_pages"

    rv = client.get(jobs_index_page.url)

    menu = rv.context_data["menu_pages"]
    assert len(menu) == 1
    assert menu[0]["page"].specific == jobs_index_page


def test_menu_pages_live(jobs_index_page):
    "Should only include live pages, not draft ones"

    live_job = JobPage(live=True, title="Live")
    jobs_index_page.add_child(instance=live_job)

    draft_job = JobPage(live=False, title="Live")
    jobs_index_page.add_child(instance=draft_job)

    rv = client.get(jobs_index_page.url)

    menu = rv.context_data["menu_pages"]
    assert len(menu) == 1
    assert menu[0]["page"].specific == jobs_index_page

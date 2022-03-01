import pytest

from django.test import Client

from modules.content.models import ArticlePage, JobPage


pytestmark = pytest.mark.django_db

client = Client()


def test_menu_pages_siblings(jobs_index_page):
    "Should include all the page's siblings"

    parent = jobs_index_page.get_parent()

    article_1 = ArticlePage(live=True, title="Article 1")
    parent.add_child(instance=article_1)

    article_2 = ArticlePage(live=True, title="Article 2")
    parent.add_child(instance=article_2)

    # Shouldn't be included:
    draft_article = ArticlePage(live=False, title="Draft article")
    parent.add_child(instance=draft_article)

    rv = client.get(jobs_index_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu) == 3
    assert menu[0]["page"].specific == jobs_index_page
    assert menu[1]["page"].specific == article_1
    assert menu[2]["page"].specific == article_2


def test_menu_pages_children(jobs_index_page):
    "Should include any child pages"

    job_1 = JobPage(live=True, title="Job 1")
    jobs_index_page.add_child(instance=job_1)

    job_2 = JobPage(live=True, title="Job 2")
    jobs_index_page.add_child(instance=job_2)

    # Shouldn't be included:
    draft_job = JobPage(live=False, title="Draft job")
    jobs_index_page.add_child(instance=draft_job)

    rv = client.get(jobs_index_page.url)

    menu = rv.context_data['menu_pages']

    assert len(menu[0]["children"]) == 2
    assert menu[0]["children"][0].specific == job_1
    assert menu[0]["children"][1].specific == job_2

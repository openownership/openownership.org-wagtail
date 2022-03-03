import pytest

from django.test import Client

from modules.content.models import TagPage, TaxonomyPage
from modules.taxonomy.models import FocusAreaTag


pytestmark = pytest.mark.django_db

client = Client()


def test_context_live(taxonomy_page):
    "Should only show live pages"

    tag1 = FocusAreaTag(name='Cats')
    tag1.save()
    tag2 = FocusAreaTag(name='Dogs')
    tag2.save()

    live_page = TagPage(live=True, title='Cats', focus_area=tag1)
    taxonomy_page.add_child(instance=live_page)
    live_page.save()

    draft_page = TagPage(live=False, title='Dogs', focus_area=tag2)
    taxonomy_page.add_child(instance=draft_page)
    live_page.save()

    rv = client.get(taxonomy_page.url)

    pages = rv.context_data['pages']
    assert len(pages) == 1
    assert pages[0].specific == live_page


def test_context_children(taxonomy_page):
    "Should only show child pages"

    tag1 = FocusAreaTag(name='Cats')
    tag1.save()

    page1 = TagPage(live=True, title='Cats', focus_area=tag1)
    taxonomy_page.add_child(instance=page1)
    page1.save()

    # Make a new taxonomy page:
    parent = taxonomy_page.get_parent()
    taxonomy_page_2 = TaxonomyPage(live=True, title="Tax 2")
    parent.add_child(instance=taxonomy_page_2)
    taxonomy_page_2.save()

    # And a new page under that, which shouldn't appear.
    page2 = TagPage(live=True, title='Cats 2', focus_area=tag1)
    taxonomy_page_2.add_child(instance=page2)
    page2.save()

    rv = client.get(taxonomy_page.url)

    pages = rv.context_data['pages']
    assert len(pages) == 1
    assert pages[0].specific == page1

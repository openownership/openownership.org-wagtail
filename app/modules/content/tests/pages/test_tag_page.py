import pytest

from django.test import Client

from modules.content.models import PublicationFrontPage, SectionPage, TagPage, TaxonomyPage
from modules.taxonomy.models import FocusAreaTag, FocusAreaTaggedPage, PublicationType


pytestmark = pytest.mark.django_db

client = Client()


def test_category_context_live(tag_page):
    "Category page should only show live pages"

    section_page = tag_page.get_parent().get_parent()

    category = PublicationType.objects.create(name='Case study')
    tag_page.publication_type = category
    tag_page.save()

    live_pub = PublicationFrontPage(
        live=True, title="Live", publication_type=category
    )
    section_page.add_child(instance=live_pub)
    live_pub.save_revision().publish()

    draft_pub = PublicationFrontPage(
        live=False, title="Draft", publication_type=category
    )
    section_page.add_child(instance=draft_pub)
    draft_pub.save_revision()

    rv = client.get(tag_page.url)

    pages = rv.context_data['page_obj'].object_list
    assert len(pages) == 1
    assert pages[0].specific == live_pub


def test_category_context_from_all_sections(tag_page):
    "Cagegory page should show pagess from all sections"

    section_page = tag_page.get_parent().get_parent()

    section_2 = SectionPage(live=True, title="Section 2")
    section_page.get_parent().add_child(instance=section_2)
    section_2.save()

    category = PublicationType.objects.create(name='Case study')
    tag_page.publication_type = category
    tag_page.save()

    # A page in the same section as the tag page
    pub1 = PublicationFrontPage(
        live=True, title="Pub 1", publication_type=category
    )
    section_page.add_child(instance=pub1)
    pub1.save_revision().publish()

    # A page in the second section
    pub2 = PublicationFrontPage(
        live=True, title="Pub 2", publication_type=category
    )
    section_2.add_child(instance=pub2)
    pub2.save_revision().publish()

    rv = client.get(tag_page.url)

    pages = [p.specific for p in rv.context_data['page_obj'].object_list]
    assert len(pages) == 2
    assert pub1 in pages
    assert pub2 in pages


def test_tag_context_live(tag_page):
    "Tag page should only show live pages"

    section_page = tag_page.get_parent().get_parent()

    tag = FocusAreaTag.objects.create(name='Cats')
    tag_page.focus_area = tag
    tag_page.save()

    live_pub = PublicationFrontPage(live=True, title="Live")
    section_page.add_child(instance=live_pub)
    live_pub.save_revision().publish()
    FocusAreaTaggedPage.objects.create(tag=tag, content_object=live_pub)

    draft_pub = PublicationFrontPage(live=False, title="Draft")
    section_page.add_child(instance=draft_pub)
    draft_pub.save_revision()
    FocusAreaTaggedPage.objects.create(tag=tag, content_object=live_pub)

    rv = client.get(tag_page.url)

    pages = rv.context_data['page_obj'].object_list
    assert len(pages) == 1
    assert pages[0].specific == live_pub

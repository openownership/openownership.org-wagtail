import pytest

from django.test import Client

from modules.content.models import (
    BlogArticlePage,
    PressLink,
    SectionPage,
)
from modules.taxonomy.models import (
    FocusAreaTag,
    FocusAreaTaggedPage,
    PublicationType,
    SectorTag,
    SectorTaggedPage,
)


pytestmark = pytest.mark.django_db

client = Client()


# The menu_pages() method is common to all the taxonomy.views and is
# a bit complex, so we're testing it here, in one place.


def test_no_children(section_page):
    "By default there should be only a link to the section page"
    rv = client.get('/en/section/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1
    assert pages[0]["page"].specific == section_page


#######################################################################
# Areas of focus


def test_areas_of_focus(blog_index_page):
    "If there's any content with an Area of Focus tag, the link to tag should be there"

    cats_tag = FocusAreaTag.objects.create(name='Cats')
    cats_post = BlogArticlePage(live=True, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()
    FocusAreaTaggedPage.objects.create(tag=cats_tag, content_object=cats_post)

    rv = client.get('/en/section/focus-areas/cats/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 3

    assert pages[1]["page"].title == "Area of Focus"
    assert pages[1]["page"].pk == "TaxonomyView-section-FocusAreaTag"
    assert len(pages[1]["children"]) == 1
    assert pages[1]["children"][0].title == "Cats"
    assert pages[1]["children"][0].pk == "TaxonomyPagesView-section-FocusAreaTag-cats"
    assert pages[1]["children"][0].url == "/en/section/focus-areas/cats/"

    # This will also be there:
    assert pages[2]["page"].title == "Latest Section"


def test_areas_of_focus_live_only(blog_index_page):
    "Link should not be there if only content with Area of Focus tag is not live"

    cats_tag = FocusAreaTag.objects.create(name='Cats')
    cats_post = BlogArticlePage(live=False, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision()
    FocusAreaTaggedPage.objects.create(tag=cats_tag, content_object=cats_post)

    rv = client.get('/en/section/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1


def test_areas_of_focus_in_section_only(blog_index_page):
    "Link should not be there if only content with Area of Focus tag is in different section"

    cats_tag = FocusAreaTag.objects.create(name='Cats')
    cats_post = BlogArticlePage(live=True, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()
    FocusAreaTaggedPage.objects.create(tag=cats_tag, content_object=cats_post)

    grandparent = blog_index_page.get_parent().get_parent()

    section_2 = SectionPage(live=True, title="Section 2", slug='section-2')
    grandparent.add_child(instance=section_2)
    section_2.save_revision().publish()

    # Make a request to section 2:
    rv = client.get('/en/section-2/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1


#######################################################################
# Sectors


def test_sectors(blog_index_page):
    "If there's any content with a Sector tag, the link to the tag should be there"

    cats_tag = SectorTag.objects.create(name='Cats')
    cats_post = BlogArticlePage(live=True, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()
    SectorTaggedPage.objects.create(tag=cats_tag, content_object=cats_post)

    rv = client.get('/en/section/sectors/cats/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 3

    assert pages[1]["page"].title == "Sector"
    assert pages[1]["page"].pk == "TaxonomyView-section-SectorTag"
    assert len(pages[1]["children"]) == 1
    assert pages[1]["children"][0].title == "Cats"
    assert pages[1]["children"][0].pk == "TaxonomyPagesView-section-SectorTag-cats"
    assert pages[1]["children"][0].url == "/en/section/sectors/cats/"

    # This will also be there:
    assert pages[2]["page"].title == "Latest Section"


def test_sectors_live_only(blog_index_page):
    "Link should not be there if only content with Sector tag is not live"

    cats_tag = SectorTag.objects.create(name='Cats')
    cats_post = BlogArticlePage(live=False, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision()
    SectorTaggedPage.objects.create(tag=cats_tag, content_object=cats_post)

    rv = client.get('/en/section/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1


def test_sectors_in_section_only(blog_index_page):
    "Link should not be there if only content with Sector tag is in different section"

    cats_tag = SectorTag.objects.create(name='Cats')
    cats_post = BlogArticlePage(live=True, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()
    SectorTaggedPage.objects.create(tag=cats_tag, content_object=cats_post)

    grandparent = blog_index_page.get_parent().get_parent()

    section_2 = SectionPage(live=True, title="Section 2", slug='section-2')
    grandparent.add_child(instance=section_2)
    section_2.save_revision().publish()

    # Make a request to section 2:
    rv = client.get('/en/section-2/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1


#######################################################################
# Publication type


def test_publication_types(blog_index_page):
    "If there's any content with a Publication Type, the link to the type should be there"

    cats_category = PublicationType.objects.create(name='Cats')
    cats_post = BlogArticlePage(
        live=True, title="Cats post", publication_type=cats_category
    )
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()

    rv = client.get('/en/section/types/cats/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 3

    assert pages[1]["page"].title == "Publication type"
    assert pages[1]["page"].pk == "TaxonomyView-section-PublicationType"
    assert len(pages[1]["children"]) == 1
    assert pages[1]["children"][0].title == "Cats"
    assert pages[1]["children"][0].pk == "TaxonomyPagesView-section-PublicationType-cats"
    assert pages[1]["children"][0].url == "/en/section/types/cats/"

    # This will also be there:
    assert pages[2]["page"].title == "Latest Section"


def test_publication_types_live_only(blog_index_page):
    "Link should not be there if only content with Publication Type tag is not live"

    cats_category = PublicationType.objects.create(name='Cats')
    cats_post = BlogArticlePage(
        live=False, title="Cats post", publication_type=cats_category
    )
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision()

    rv = client.get('/en/section/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1


def test_sectors_in_section_only(blog_index_page):
    "Link should not be there if only content with Publication Type is in different section"

    cats_category = PublicationType.objects.create(name='Cats')
    cats_post = BlogArticlePage(
        live=True, title="Cats post", publication_type=cats_category
    )
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()

    grandparent = blog_index_page.get_parent().get_parent()

    section_2 = SectionPage(live=True, title="Section 2", slug='section-2')
    grandparent.add_child(instance=section_2)
    section_2.save_revision().publish()

    # Make a request to section 2:
    rv = client.get('/en/section-2/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1


#######################################################################
# Latest


def test_latest(blog_index_page):
    "It should include a Latest link if there's any content, tagged or not"

    cats_post = BlogArticlePage(live=True, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()

    rv = client.get('/en/section/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 2
    assert pages[1]["page"].title == "Latest Section"
    assert pages[1]["page"].pk == "SectionLatestPagesView-section"


def test_latest_live_only(blog_index_page):
    "It should not include a Latest link if the only content isn't live"

    cats_post = BlogArticlePage(live=False, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision()

    rv = client.get('/en/section/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1


def test_latest_in_section_only(blog_index_page):
    "It should not include a Latest link if the only content is in a different section"

    # A post in the original section:
    cats_post = BlogArticlePage(live=True, title="Cats post")
    blog_index_page.add_child(instance=cats_post)
    cats_post.save_revision().publish()

    grandparent = blog_index_page.get_parent().get_parent()

    section_2 = SectionPage(live=True, title="Section 2", slug='section-2')
    grandparent.add_child(instance=section_2)
    section_2.save_revision().publish()

    # Make a request to section 2:
    rv = client.get('/en/section-2/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1


#######################################################################
# Press links


def test_press_links(section_page):
    "It should include a link to Press Links"

    PressLink.objects.create(title="Link", section_page=section_page)

    rv = client.get('/en/section/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 2
    assert pages[1]["page"].title == "Press links"
    assert pages[1]["page"].pk == "SectionPressLinksView-section"


def test_press_links_in_section_only(section_page):
    "It should not include a link to Press Links if the only links are in a different section"

    parent = section_page.get_parent()

    section_2 = SectionPage(live=True, title="Section 2", slug='section-2')
    parent.add_child(instance=section_2)
    section_2.save_revision().publish()

    PressLink.objects.create(title="Link", section_page=section_2)

    rv = client.get('/en/section/latest/')

    pages = rv.context_data['menu_pages']
    assert len(pages) == 1






    # section_page = blog_index_page.get_parent()

    # cats_tag = SectorTag.objects.create(name='Cats')
    # cats_post = BlogArticlePage(live=True, title="Cats post")
    # blog_index_page.add_child(instance=cats_post)
    # cats_post.save_revision().publish()
    # SectorTaggedPage.objects.create(tag=cats_tag, content_object=cats_post)

    # assert pages[0]["page"].specific == section_page

    # assert pages[1]["page"].title == "Area of Focus"
    # assert pages[1]["page"].pk == "TaxonomyView-section-FocusAreaTag"
    # assert pages[1]["children"] == []

    # assert pages[2]["page"].title == "Sector"
    # assert pages[2]["page"].pk == "TaxonomyView-section-SectorTag"
    # assert len(pages[2]["children"]) == 1
    # assert pages[2]["children"][0].title == "Cats"
    # assert pages[2]["children"][0].pk == "TaxonomyPagesView-section-SectorTag-cats"
    # assert pages[2]["children"][0].url == "/en/section/sectors/cats/"

    # assert pages[3]["page"].title == "Publication type"
    # assert pages[3]["page"].pk == "TaxonomyView-section-PublicationType"
    # assert pages[3]["children"] == []

    # assert pages[4]["page"].title == "Latest Section"
    # assert pages[4]["page"].pk == "SectionLatestPagesView-section"

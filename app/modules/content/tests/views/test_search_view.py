import pytest
from django.test import RequestFactory
from wagtail.models import Page

from modules.content.models import PublicationInnerPage
from modules.content.views import SearchView
from modules.taxonomy.models import PublicationType

pytestmark = pytest.mark.django_db

factory = RequestFactory()

# Every filter parameter the search view reads, each an id list.
FILTER_PARAMS = ("pt", "pr", "sn", "sr", "co")


def filtered_view(query: str) -> SearchView:
    """A view with its filters read from a query string."""
    view = SearchView()
    view.filters_list = []
    view._set_filters(factory.get(f"/search/?{query}"))
    return view


def test_restrict_excludes_inner_pages(publication_front_page):
    """The search result queryset must drop PublicationInnerPage rows so child
    pages never surface; the parent front page is kept.
    """
    parent = publication_front_page
    inner = PublicationInnerPage(live=True, title="Inner Chapter")
    parent.add_child(instance=inner)
    inner.save_revision().publish()

    view = SearchView()
    result_ids = [page.id for page in view._restrict(Page.objects, [])]

    assert inner.id not in result_ids
    assert parent.id in result_ids


####################################################################################################
# Filter parameters are user input
####################################################################################################

# This is a public URL. A stale bookmark, a mangled share link or a crawler
# guessing at parameters should show results, never a 500.


@pytest.mark.parametrize("param", FILTER_PARAMS)
def test_a_non_numeric_filter_value_is_ignored(param):
    view = filtered_view(f"{param}=banana")

    assert view.filters_list == []


@pytest.mark.parametrize("param", FILTER_PARAMS)
def test_an_empty_filter_value_is_ignored(param):
    view = filtered_view(f"{param}=")

    assert view.filters_list == []


def test_a_good_value_survives_a_bad_one_beside_it():
    """One broken value in a share link should not throw away the rest."""
    wanted = PublicationType.objects.create(name="Guidance", slug="guidance")

    view = filtered_view(f"pt=banana&pt={wanted.id}")

    assert list(view.filters["publication_types"]) == [wanted]


def test_a_real_filter_still_works():
    wanted = PublicationType.objects.create(name="Case study", slug="case-study")

    view = filtered_view(f"pt={wanted.id}")

    assert list(view.filters["publication_types"]) == [wanted]
    assert view.is_filtered is True


def test_no_filters_at_all_is_not_filtered():
    view = filtered_view("")

    assert view.filters_list == []
    assert getattr(view, "is_filtered", False) is False

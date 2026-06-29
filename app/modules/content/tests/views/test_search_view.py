from wagtail.models import Page

from modules.content.models import PublicationInnerPage
from modules.content.views import SearchView


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

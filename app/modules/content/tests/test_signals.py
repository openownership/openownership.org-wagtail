import pytest

from modules.content.models import PublicationInnerPage

pytestmark = pytest.mark.django_db


def _spy_on_reindex(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "wagtail.search.index.insert_or_update_object",
        lambda obj: calls.append(obj),
    )
    return calls


def _add_inner(parent):
    inner = PublicationInnerPage(live=True, title="Inner Chapter")
    parent.add_child(instance=inner)
    inner.save_revision().publish()
    return inner


def test_publishing_inner_page_reindexes_parent(publication_front_page, monkeypatch):
    calls = _spy_on_reindex(monkeypatch)
    _add_inner(publication_front_page)
    assert any(getattr(c, "pk", None) == publication_front_page.pk for c in calls)


def test_unpublishing_inner_page_reindexes_parent(publication_front_page, monkeypatch):
    inner = _add_inner(publication_front_page)
    calls = _spy_on_reindex(monkeypatch)  # spy after publish, so we only capture the unpublish
    inner.unpublish()
    assert any(getattr(c, "pk", None) == publication_front_page.pk for c in calls)


def test_deleting_inner_page_reindexes_parent(publication_front_page, monkeypatch):
    inner = _add_inner(publication_front_page)
    calls = _spy_on_reindex(monkeypatch)
    inner.delete()
    assert any(getattr(c, "pk", None) == publication_front_page.pk for c in calls)
